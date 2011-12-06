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

from logging import getLogger

from flask import Flask

from .logger import setup_logging

setup_logging( __name__ )
app = Flask( __name__ )

LOGGER = getLogger( __name__ )

@app.route( '/' )
def index():
	LOGGER.debug( 'This is an application log message' )	
	return 'Hello, world!'