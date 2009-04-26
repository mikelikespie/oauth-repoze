This file is for you to describe the oauth-what application. Typically
you would include information such as the information below:

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
	
