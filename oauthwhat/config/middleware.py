"""Pylons middleware initialization"""
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StatusCodeRedirect
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware

from oauthwhat.config.environment import load_environment

def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether this application provides a full WSGI stack (by default,
        meaning it handles its own exceptions and errors). Disable
        full_stack when this application is "managed" by another WSGI
        middleware.

    ``static_files``
        Whether this application serves its own static files; disable
        when another web server is responsible for serving them.

    ``app_conf``
        The application's local configuration. Normally specified in
        the [app:<name>] section of the Paste ini file (where <name>
        defaults to main).

    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI apGp
    app = PylonsApp()

    # Routing/Session/Cache Middleware
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)

    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
    app = add_auth(app, config)

    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    if asbool(static_files):
        # Serve static files
        static_app = StaticURLParser(config['pylons.paths']['static_files'])
        app = Cascade([static_app, app])

    return app

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

    from oauthwhat.lib.repoze.who.oauth.identification import OAuthIdentificationPlugin
    from oauthwhat.lib.repoze.who.oauth.classifiers import oauth_challenge_decider
    from oauthwhat.lib.oauth import OAuthTwitterConsumer

    from repoze.what.middleware import setup_auth
    from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

    
    OAuthTwitterConsumer.consumer_key = config['oauth.consumer_key']
    OAuthTwitterConsumer.consumer_secret = config['oauth.consumer_secret']

    # Defining the group adapters; you may add as much as you need:
    #groups = {'all_groups': HtgroupsAdapter('/path/to/groups.htgroups')}

    # Defining the permission adapters; you may add as much as you need:
    #permissions = {'all_perms': INIPermissionsAdapter('/path/to/perms.ini')}

    # repoze.who identifiers; you may add as much as you need:
    #basicauth = BasicAuthPlugin('Private web site')
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
        #groups,
        #permissions,
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        challenge_decider=oauth_challenge_decider)
    return app_with_auth

