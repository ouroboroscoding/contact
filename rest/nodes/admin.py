# coding=utf8
""" Admin REST

Handles starting the REST server using the Admin service
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-08-25"

# Ouroboros imports
from body import register_services, REST
from config import config
import record_mysql

# Project imports
from . import errors
from services.admin import Admin

def main():
	"""Main

	Starts the http REST server
	"""

	# Add the primary host
	record_mysql.add_host(config.mysql.primary({
		'charset': 'utf8',
		'host': 'localhost',
		'passwd': '',
		'port': 3306,
		'user': 'mysql'
	}))

	# Get the config
	dConf = config.admin({
		'verbose': False
	})

	# Init the service
	oAdmin = Admin()

	# Register the services
	oRest = register_services({ 'admin': oAdmin })

	# Run the REST server with the Client instance
	REST(
		'admin',
		oAdmin,
		config.body.rest.allowed('contact.local'),
		errors,
		dConf['verbose']
	).run(
		host = oRest['admin']['host'],
		port = oRest['admin']['port'],
		workers = oRest['admin']['workers'],
		timeout = 'timeout' in oRest['admin'] and \
			oRest['admin']['timeout'] or 30
	)

# Only run if called directly
if __name__ == '__main__':
	main()