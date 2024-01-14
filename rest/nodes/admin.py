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

	# Get the admin conf
	dAdmin = oRest['admin']

	# Run the REST server with the Client instance
	REST(
		name = 'admin',
		instance = oAdmin,
		cors = config.body.rest.allowed(),
		lists = True,
		on_errors = errors,
		verbose = dConf['verbose']
	).run(
		host = dAdmin['host'],
		port = dAdmin['port'],
		workers = dAdmin['workers'],
		timeout = 'timeout' in dAdmin and \
			dAdmin['timeout'] or 30
	)

# Only run if called directly
if __name__ == '__main__':
	main()