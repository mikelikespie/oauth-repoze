import zope.interface 
from repoze.who.interfaces import IChallengeDecider


def oauth_challenge_decider(environ, status, headers):
    environ['repoze.who.logger'].debug('in challenge_decider')
    # we do the default if it's a 401, probably we show a form then
    if status.startswith('401 '):
        return True
    elif environ.has_key('repoze.whoplugins.oauth.oauth_request_token'):
        # in case IIdentification found an oauth it should be in the environ
        # and we do the challenge
        return True
    return False
    
zope.interface.directlyProvides(oauth_challenge_decider, IChallengeDecider)

