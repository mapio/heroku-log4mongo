# Copyright 2011, Massimo Santini <santini@dsi.unimi.it>
# 
# This file is part of "free-logging".
# 
# "No Fuss Bookmarks" is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# "free-logging" is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# "free-logging". If not, see <http://www.gnu.org/licenses/>.

from logging import INFO, getLogger, StreamHandler, Formatter, DEBUG, INFO
from os import environ
from urlparse import urlparse

from gunicorn.glogging import Logger
from log4mongo.handlers import MongoHandler, MongoFormatter


# parse the MONGOLAB_URI environment variable to get the auth/db info

MONGOLAB_URI_PARSED = urlparse( environ[ 'MONGOLAB_URI' ] )
MONGOLAB_CONF_DICT = dict( 
	host = MONGOLAB_URI_PARSED.hostname, 
	port = MONGOLAB_URI_PARSED.port, 
	database_name = MONGOLAB_URI_PARSED.path[ 1: ],
	username = MONGOLAB_URI_PARSED.username, 
	password = MONGOLAB_URI_PARSED.password
)

# determine if we are running in production (e.g., on Heroku), or locally

PRODUCTION = environ[ 'VERSION' ] == 'production'


# setup the root logger so that application logs go to mongolab

def setup_logging( name ):
	root_logger = getLogger( name )
	if PRODUCTION:
		handler = MongoHandler( level = DEBUG, collection = 'application-log', **MONGOLAB_CONF_DICT )
		handler.setFormatter( MongoFormatter() )
	else:
		handler = StreamHandler()
		handler.setLevel( DEBUG )
		handler.setFormatter( Formatter( '%(asctime)s [%(process)d] [%(levelname)s/APPLICATION] %(message)s', '%Y.%m:%d %H:%M:%S' ) )
	root_logger.setLevel( DEBUG )
	root_logger.addHandler( handler )

# define a logger so that gunicorn sends access and error logs to mongolab

class GunicornLogger( Logger ):
	def __init__( self, cfg ):
		super( GunicornLogger, self ).__init__( cfg )
		if PRODUCTION:
			access_handler = MongoHandler( level = INFO, collection = 'access-log', **MONGOLAB_CONF_DICT )
			error_handler = MongoHandler( level = INFO, collection = 'error-log', **MONGOLAB_CONF_DICT )
			access_handler.setFormatter( MongoFormatter() )
			error_handler.setFormatter( MongoFormatter() )
			self.error_log.addHandler( error_handler )
			self.error_log.setLevel( INFO )
		else:
			access_handler = StreamHandler()
			access_handler.setFormatter( Formatter( '%(asctime)s [%(process)d] [%(levelname)s/ACCESS] %(message)s', '%Y.%m:%d %H:%M:%S' ) )
		self.access_log.addHandler( access_handler )
		self.access_log.setLevel( INFO )
