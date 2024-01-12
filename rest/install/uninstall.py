# coding=utf8
""" Records

Installs the database and tables required by the record instances
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-08-26"

# Ouroboros imports
from config import config
import record_mysql
import record_redis

# Records
from records.admin import category, contact, project, unsubscribe

# Only run if called directly
if __name__ == '__main__':

	# Add the "_" host
	record_mysql.add_host(config.mysql.primary({
		'charset': 'utf8',
		'host': 'localhost',
		'passwd': '',
		'port': 3306,
		'user': 'mysql'
	}))

	# Delete the User table
	category.Category.uninstall()
	contact.Contact.uninstall()
	project.Project.uninstall()
	unsubscribe.Unsubscribe.uninstall()

	# Add the DB
	record_mysql.db_drop(
		config.mysql.db('contact')
	)