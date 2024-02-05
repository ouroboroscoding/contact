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
from records.contact import \
	campaign, campaign_contact, category, contact, project, sender

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

	# Add the DB
	record_mysql.db_create(
		config.mysql.db('contact')
	)

	# Create the tables
	campaign.Campaign.install()
	campaign_contact.CampaignContact.install()
	category.Category.install()
	contact.Contact.install()
	project.Project.install()
	sender.Sender.install()