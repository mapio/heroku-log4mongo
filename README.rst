heroku-log4mongo
================

.. |flattr| image:: http://api.flattr.com/button/flattr-badge-large.png
  :alt: Flattr this git repo
  :target: https://flattr.com/submit/auto?user_id=mapio&url=https://github.com/mapio/heroku-log4mongo&title=heroku-log4mongo&language=en_GB&tags=github&category=software

|flattr| 

`heroku-log4mongo` is an hack to obain 240Mb of free cloud logging for your
Heroku apps, it's (a very rough, no fancy interface, no fun) *free version* of
`Loggly <http://addons.heroku.com/loggly>`_ service, but with indefinite *data
retention*.

First of all you need to setup your Heroku environment as usual::

  $ git init
  $ heroku create --stack cedar

In the example of this repo we'll now use `Flask <http://flask.pocoo.org/>`_
to setup a minimalistic app, every other framework will do (albeit being less
a pleasure to use – I admit loving Flask).

In particular, you need to have at least these lines in your
`requirements.txt` file::

  gunicorn
  log4mongo

plus, of course, Flask and other packages your app depends upon.

The key here is the very nice `log4mongo
<https://github.com/log4mongo/log4mongo-python>`_ library that very easily
allows you to use a (free) `mongolab <https://mongolab.com/home>`_ databse as
a logging endpoint.

Now install the packages locally (after creating a suitable `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ with `virtualenvwrapper
<http://www.doughellmann.com/projects/virtualenvwrapper/>`_)::

  $ mkvirtualenv heroku-log4mongo
  $ pip install -r requirements.txt

Now add the *free* `mongolab:starter` addon to your Heroku app::

  $ heroku addons:add mongolab:starter

that will give you 240Mb

To use it locally, for testing purposes, you need to obtain the URL of the
just created db, you can get it with:

  $ heroku config -s | grep 'MONGOLAB_URI' > .env

that will save it in `.env` file so that `foreman
<https://github.com/ddollar/foreman>`_ will pick it up when running your
application locally (as will Heroku do on their side to run your app).

Now, to use the databse with log4mongo a bit of effort is needed since URI are
not directlly supported; but it's enough to use standard library tools:

    from os import environ
    from urlparse import urlparse
    
    MONGOLAB_URI_PARSED = urlparse( environ[ 'MONGOLAB_URI' ] )
    MONGOLAB_CONF_DICT = dict( 
        host = MONGOLAB_URI_PARSED.hostname, 
        port = MONGOLAB_URI_PARSED.port, 
        database_name = MONGOLAB_URI_PARSED.path[ 1: ],
        username = MONGOLAB_URI_PARSED.username, 
        password = MONGOLAB_URI_PARSED.password
    )

Now, you can configure a logger to use mongolab in a breeze

    from logging import getLogger, DEBUG
    from log4mongo.handlers import MongoHandler
    
    logger = getLogger( name )
    logger.addHandler( MongoHandler( level = DEBUG, collection = 'application-log', **MONGOLAB_CONF_DICT ) )

and your log messages to `logger` will go to your mongolab db.

You can also trick gunicorn to send to mongolab db its access and error logs.
To do this you need to put the following in your `Procfile`::

  web: gunicorn fl:app --logger-class=<MONGO_LOGGER> --access-logfile=/dev/null --error-logfile=- -w 3 -b "0.0.0.0:$PORT"

(it's important to define the `access-logile` option, otherwise the
configuration will not setup the needed handlers), where `<MONGO_LOGGER>` is
the name of a logging class similar to this one::

  from gunicorn.glogging import Logger
  from log4mongo.handlers import MongoHandler, MongoFormatter
  
  class GunicornLogger( Logger ):
    def __init__( self, cfg ):
        super( GunicornLogger, self ).__init__( cfg )
        access_handler = MongoHandler( level = INFO, collection = 'access-log', **MONGOLAB_CONF_DICT )
        error_handler = MongoHandler( level = INFO, collection = 'error-log', **MONGOLAB_CONF_DICT )
        access_handler.setFormatter( MongoFormatter() )
        error_handler.setFormatter( MongoFormatter() )
        self.error_log.addHandler( error_handler )
        self.error_log.setLevel( INFO )
        access_handler = StreamHandler()
        access_handler.setFormatter( Formatter( '%(asctime)s [%(process)d] [%(levelname)s/ACCESS] %(message)s', '%Y.%m:%d %H:%M:%S' ) )
        self.access_log.addHandler( access_handler )
        self.access_log.setLevel( INFO )

You can also configure logging to depend on the `VERSION` of the application,
by making local loggin to standard output, and the production one to mongolab.
