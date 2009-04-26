import repoze
import repoze.what
import repoze.what.middleware

from repoze.what.middleware import setup_auth
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from oauthwhat.lib.oauth import OAuthTwitterConsumer
from oauthwhat.lib.repoze.who.oauth.classifiers import oauth_challenge_decider
from oauthwhat.lib.repoze.who.oauth.identification import OAuthIdentificationPlugin


def add_auth(app, config):
    """
    Add authentication and authorization middleware to the ``app``.

    :param app: The WSGI application.
    :return: The same WSGI application, with authentication and
        authorization middleware.

    People will login using HTTP Authentication and their credentials are
    kept in an ``Htpasswd`` file. For authorization through repoze.what,
    we load our groups stored in an ``Htgroups`` file and our permissions
    stored in an ``.ini`` file.

    """

    
    OAuthTwitterConsumer.consumer_key = config['oauth.consumer_key']
    OAuthTwitterConsumer.consumer_secret = config['oauth.consumer_secret']

    oauth = OAuthIdentificationPlugin(OAuthTwitterConsumer,
                                        login_handler_path = '/login',
                                        logout_handler_path = '/logout',
                                        login_form_url = '/login_form',
                                        logged_in_url = '/main',
                                        came_from_field = 'came_from',
                                        rememberer_name='auth_tkt')

    identifiers = [('oauth', oauth), ('auth_tkt', AuthTktCookiePlugin('secret', 'auth_tkt'))]

    authenticators = [('oauth', oauth)]

    # repoze.who challengers; you may add as much as you need:
    challengers = [('oauth', oauth)]

    permissions = {}
    groups = {}

    app_with_auth = setup_auth(
        app,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        challenge_decider=oauth_challenge_decider)
    return app_with_auth

