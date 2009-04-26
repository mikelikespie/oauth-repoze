This is a demo of OAuth with pylons using repoze.what/who middleware

It's not polished by any means, but should be a good starting point

The interesting oauth tidbits are in::

	oauthwhat.lib.auth
	oauthwhat.lib

As well as a little in

	oauth.model

Installation and Setup
======================

Install ``oauth-what`` using easy_install::

    easy_install oauth-what

Make a config file as follows::

    paster make-config oauth-what config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.

Make sure you update::

	oauth.consumer_key = CONSUMER_KEY_HERE
	oauth.consumer_secret = SECRET_KEY_HERE

With your keys from your oauth provider

Send questions/comments to mikelikespie@gmail.com

Thanks to Chrstian Scholtz for the repoze.who.openid plugin which I tore apart http://quantumcore.org/docs/repoze.who.plugins.openid
	
