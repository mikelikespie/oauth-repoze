import logging

from oauthwhat.lib.base import BaseController, render
from oauthwhat.lib.oauth import OAuthTwitterConsumer
from repoze.what.predicates import not_anonymous
from repoze.what.plugins.pylonshq import ActionProtector

from pylons import request
from pylons import tmpl_context as c

log = logging.getLogger(__name__)

class DemoController(BaseController):

    @ActionProtector(not_anonymous())
    def index(self):
        # Return a rendered template
        #return render('/demo.mako')
        # or, return a response
        consumer = OAuthTwitterConsumer(request.environ['repoze.who.identity']['repoze.who.userid'])
        c.userid = consumer.token.specifier
        return render('/logged-in.html')

    def login_form(self):
        return render('/sign-in.html')
