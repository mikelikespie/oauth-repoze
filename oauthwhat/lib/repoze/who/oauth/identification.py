#Code comes originall from http://quantumcore.org/docs/repoze.who.plugins.openid/
import cgi
import urlparse
import cgitb
import sys
from zope.interface import implements

from repoze.who.interfaces import IChallenger
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IAuthenticator

from webob import Request, Response



class OAuthIdentificationPlugin(object):
    """The repoze.who OAuth plugin
    
    This class contains 3 plugin types and is thus implementing
    IIdentifier, IChallenger and IAuthenticator.
    (check the `repoze.who documentation <http://static.repoze.org/bfgdocs/>`_
    for what all these plugin types do.)
    
    """


    implements(IChallenger, IIdentifier, IAuthenticator)

    def __init__(self,
                    oauth_consumer,
                    error_field = '',
                    store_file_path='',
                    session_name = '',
                    login_handler_path = '',
                    logout_handler_path = '',
                    login_form_url = '',
                    logged_in_url = '',
                    logged_out_url = '',
                    came_from_field = '',
                    rememberer_name = ''):

        self.oauth_consumer = oauth_consumer
        self.rememberer_name = rememberer_name
        self.login_handler_path = login_handler_path
        self.logout_handler_path = logout_handler_path
        self.login_form_url = login_form_url
        self.session_name = session_name
        self.error_field = error_field
        self.came_from_field = came_from_field
        self.logged_out_url = logged_out_url
        self.logged_in_url = logged_in_url
        
    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    def get_consumer(self, token):
        return self.oauth_consumer(token)
        
    def redirect_to_logged_in(self, environ):
        """redirect to came_from or standard page if login was successful"""
        request = Request(environ)
        came_from = request.params.get(self.came_from_field,'')
        if came_from!='':
            url = came_from
        else:
            url = self.logged_in_url
        res = Response()
        res.status = 302
        res.location = url
        environ['repoze.who.application'] = res    

    # IIdentifier
    def identify(self, environ):
        """this method is called when a request is incoming.

        After the challenge has been called we might get here a response
        from an oauth provider.

        """

        request = Request(environ)
        
        # first test for logout as we then don't need the rest
        if request.path == self.logout_handler_path:
            res = Response()
            # set forget headers
            for a,v in self.forget(environ,{}):
                res.headers.add(a,v)
            res.status = 302
            res.location = self.logged_out_url
            environ['repoze.who.application'] = res
            return {}

        identity = {}

        # first we check we are actually on the URL which is supposed to be the
        # url to return to (login_handler_path in configuration)
        # this URL is used for both: the answer for the login form and
        # when the oauth provider redirects the user back.
        if request.path == self.login_handler_path:

        # in the case we are coming from the login form we should have 
        # an oauth in here the user entered
            oauth_request_token = request.params.get("oauth_token", None)
            environ['repoze.who.logger'].debug('checking oauth results for : %s ' %oauth_request_token)
            
            # this part now is for the case when the oauth provider redirects
            # the user back. We should find some oauth specific fields in the request.
            if oauth_request_token is not None:
                consumer = self.get_consumer(oauth_request_token)
                #if it didn't find a token, we need to return and reauthenticate
                if not consumer.token:
                    return identity
                if not consumer.token.authorized:
                    try:
                        consumer.exchange_access_token()
                        environ['repoze.who.logger'].info('oauth request successful for : %s ' %oauth_request_token)
                    except self.oauth_consumer.AlreadyAuthorized:
                        pass
                    except Exception, exception:
                        environ['repoze.whoplugins.oauth.error'] = 'OAuth authentication failed with some sort of error %s.' %exception

                    
                # store the id for the authenticator
                identity['repoze.who.plugins.oauth.oauth_token'] = consumer.token.oauth_token
                identity['repoze.who.plugins.oauth.specifier'] = consumer.token.specifier

                # now redirect to came_from or the success page
                self.redirect_to_logged_in(environ)
                return identity
            else:
                consumer = self.oauth_consumer()
                environ['repoze.whoplugins.oauth.oauth_request_token'] = consumer.get_new_request_token()

        return identity

    # IIdentifier
    def remember(self, environ, identity):
        """remember the oauth in the session we have anyway"""
        environ['repoze.who.logger'].debug("REMEMBERING OMG")
        rememberer = self._get_rememberer(environ)
        r = rememberer.remember(environ, identity)
        return r

    # IIdentifier
    def forget(self, environ, identity):
        """forget about the authentication again"""
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    # IChallenge
    def challenge(self, environ, status, app_headers, forget_headers):
        """the challenge method is called when the ``IChallengeDecider``
        in ``classifiers.py`` returns ``True``. This is the case for either a 
        ``401`` response from the client or if the key 
        ``repoze.whoplugins.oauth.oauthrepoze.whoplugins.oauth.oauth``
        is present in the WSGI environment.
        The name of this key can be adjusted via the ``oauth_field`` configuration
        directive.

        The latter is the case when we are coming from the login page where the
        user entered the oauth to use.

        ``401`` can come back in any case and then we simply redirect to the login
        form which is configured in the who configuration as ``login_form_url``.

        """

        request = Request(environ)
        
        # now we have an oauth from the user in the request 
        environ['repoze.who.logger'].debug('starting oauth request for : %s ' % environ['repoze.whoplugins.oauth.oauth_request_token'])



        #try:
        # we create a new Consumer and start the discovery process for the URL given
        # in the library oauth_request is called auth_req btw.
        oauth_consumer = self.get_consumer(environ['repoze.whoplugins.oauth.oauth_request_token'])

           
        # not sure this can still happen but we are making sure.
        # should actually been handled by the DiscoveryFailure exception above
#        if oauth_consumer.token is None or oauth_consumer.token.authroized == False
#            environ[self.error_field] = 'OAuth should have token and authroized by now'
#            environ['repoze.who.logger'].info('OOauth should have token and authroized by now')
#            return self._redirect_to_loginform(environ)

        return_to = request.path_url # we return to this URL here
        environ['repoze.who.logger'].debug('setting return_to URL to : %s ' %return_to)

        redirect_url = oauth_consumer.get_auth_url(return_to=return_to) 
        # # , immediate=False)
        res = Response()
        res.status = 302
        res.location = redirect_url
        environ['repoze.who.logger'].debug('redirecting to : %s ' %redirect_url)

        # now it's redirecting and might come back via the identify() method
        # from the oauth provider once the user logged in there.
        return res
        
    def _redirect_to_loginform(self, environ={}):
        """redirect the user to the login form"""
        res = Response()
        res.status = 302
        q=''
        ef = environ.get(self.error_field, None)
        if ef is not None:
                q='?%s=%s' %(self.error_field, ef)
        res.location = self.login_form_url+q
        return res
        
                
    # IAuthenticator
    def authenticate(self, environ, identity):
        """dummy authenticator
        
        This takes the oauth found and uses it as the userid. Normally you would want
        to take the oauth and search a user for it to map maybe multiple oauths to a user.
        This means for you to simply implement something similar to this. 
        
        """
        if identity.has_key("repoze.who.plugins.oauth.oauth_token"):
                environ['repoze.who.logger'].info('authenticated : %s ' %identity['repoze.who.plugins.oauth.oauth_token'])
                return identity.get('repoze.who.plugins.oauth.oauth_token')


    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, id(self))

