# coding=utf8
""" Contact REST

Handles starting the REST server using the Contact service
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
from rest.services.contact import Contact

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
	dConf = config.contact({
		'verbose': False
	})

	# Init the service
	oContact = Contact()

	# Register the services
	oRest = register_services({ 'contact': oContact })

	# Get the contact conf
	dContact = oRest['contact']

	# Run the REST server with the Client instance
	REST(
		name = 'contact',
		instance = oContact,
		cors = config.body.rest.allowed(),
		lists = True,
		on_errors = errors,
		verbose = dConf['verbose']
	).run(
		host = dContact['host'],
		port = dContact['port'],
		workers = dContact['workers'],
		timeout = 'timeout' in dContact and \
			dContact['timeout'] or 30
	)

# Only run if called directly
if __name__ == '__main__':
	main()