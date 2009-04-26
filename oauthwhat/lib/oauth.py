import simplejson
import urllib
import time
import string
import random
import base64
import os
import hashlib
import urllib2
import hmac
from oauthwhat.model import OAuthToken, Session


class OAuthConsumer(object):
    request_token_url = None
    access_token_url = None
    user_auth_url = None

    #Set these manually (hella dirty hack)
    consumer_key = None
    consumer_secret = None

    class UnknownSignatureException(Exception): pass
    class UnauthorizedToken(Exception): pass
    class AlreadyAuthorized(Exception): pass

    #we have to do this so we don't get prompted with basic auth
    opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler())

    def __init__ (self, token = None):
        if token is None or isinstance(token, OAuthToken):
            self.token = token
        elif isinstance(token, str) or isinstance(token, unicode):
            self.token = Session.query(OAuthToken).filter(OAuthToken.oauth_token == token).first()

    def get_new_request_token(self):
        if self.token is not None:
            raise Exception("We already have a token, we shouldn't get here")

        token, token_secret = self._request_token()
        self.token = OAuthToken(token, token_secret)

        self.token.authorized = False
        self.token.specifier = None

        Session.add(self.token)
        Session.commit()

        return token

    def get_auth_url(self, **args):
        dat = self._gen_signed_data(self.user_auth_url, **args)

        return  self.user_auth_url + "?" + urllib.urlencode(dat)

    def _request_token(self):
        token_info = self.get_post_lines(self.request_token_url)
        dat = dict(token.split('=') for token in token_info.split('&'))
        return dat['oauth_token'], dat['oauth_token_secret']

    def exchange_access_token(self):
        if self.token.authorized:
            raise self.AlreadyAuthorized("This user has already been authorized")

        try:
            token_info = self.get_post_lines(self.access_token_url)
        except IOError, e:
            raise self.UnauthorizedToken("Has not been authorized yet")

        print token_info
        dat = dict(token.split('=') for token in token_info.split('&'))
        token, token_secret = dat['oauth_token'], dat['oauth_token_secret']

        Session.delete(self.token)

        self.token = Session.query(OAuthToken).filter(OAuthToken.oauth_token == token).first()
        
        print "Toooken"

        if self.token is None:
            self.token = OAuthToken(token, token_secret, authorized = True) 
            Session.add(self.token)

        print "getting specifier..."

        self.token.specifier = self.get_specifier()

        print "Specifier = %s" % self.token.specifier
        Session.commit()
        raise Exception()


    def _gen_signed_data(self, base_url, method="GET", sign_method='HMAC-SHA1', **params):
        args = {'oauth_consumer_key': self.consumer_key,
                'oauth_timestamp': self.__timestamp(),
                'oauth_nonce': self.__nonce(),
                'oauth_version': '1.0'}
                
        args.update(params)

        if sign_method == 'HMAC-SHA1':
            args['oauth_signature_method'] = 'HMAC-SHA1'

            key = self.consumer_secret + "&"

            if self.token is not None:
                args['oauth_token'] = self.token.oauth_token
                key += urllib.quote(self.token.oauth_token_secret, '')

            #would use urlencode, but it doesn't sort arguments
            #pargs = [sorted('%s=%s' % (k,v) for k,v in args.values())]
            message = '&'.join(
                    urllib.quote(i, '') for i in [method.upper(), base_url,
                                    urllib.urlencode(sorted(args.iteritems()))])

            args['oauth_signature'] = hmac.new(key, message, hashlib.sha1
                                                ).digest().encode('base64')[:-1]

        # Add other sign_methods here   
        else:
            raise self.UnknownSignatureException("Unknown signature method %s" % sign_method)

        return args

    def get_get(self, url, **args):
        data = self._gen_signed_data(url, method="GET", **args)
        print url, data
        uurl = "%s?%s" % (url, urllib.urlencode(data))
        print uurl
        return self.opener.open(uurl)

    def get_post(self, url, **args):
        data = self._gen_signed_data(url, method="POST", **args)
        print url, data
        return self.opener.open(url, urllib.urlencode(data))

    def get_post_lines(self, url, **args):
        f = self.get_post(url, **args)
        return ''.join(f)

    def get_specifier(self):
        raise self.NotImplemented("One must implement authentication, main class is only for authorization")

    @staticmethod
    def __randstr(leng):
        return base64.urlsafe_b64encode(os.urandom(leng))[:leng]

    @staticmethod
    def __timestamp():
        return int(time.time())

    @staticmethod
    def __nonce(leng=16):
        return OAuthConsumer.__randstr(leng)


    
class OAuthTwitterConsumer(OAuthConsumer):
    request_token_url = 'https://twitter.com/oauth/request_token'
    access_token_url = 'https://twitter.com/oauth/access_token'
    user_auth_url = 'http://twitter.com/oauth/authorize'

    twitter_verify_url = 'http://twitter.com/account/verify_credentials.json'

    default_api_prefix = 'http://twitter.com'
    default_api_suffix = '.json'

    def get_specifier(self):
        data = simplejson.load(self.get_get(self.twitter_verify_url))
        
        return data['screen_name']
