# coding=utf8
""" Admin Campaign Contact Record

Handles the campaign contact record structure
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-16"

# Ouroboros imports
from config import config
import jsonb
from record_mysql import Storage
from record_mysql.server import escape, execute, select, Select
import undefined

# Python imports
from pathlib import Path
from typing import Dict, List, Literal

# Other records
from records.admin import contact

# Create the Storage instance
CampaignContact = Storage(

	# The primary definition
	jsonb.load(
		'%s/definitions/admin/campaign_contact.json' % \
			Path(__file__).parent.parent.parent.resolve()
	),

	# The extensions necessary to store the data and revisions in MySQL
	{
		# Table related
		'__mysql__': {
			'charset': 'utf8mb4',
			'collate': 'utf8mb4_bin',
			'create': [
				'_campaign', '_contact', 'sent', 'delivered', 'opened',
				'unsubscribed'
			],
			'db': config.mysql.db('contact'),
			'indexes': {
				'ui_campaign_contact': {
					'fields': [ '_campaign', '_contact' ],
					'type': 'unique'
				},
				'i_contact': '_contact'
			},
			'name': 'admin_campaign_contact'
		}
	}
)

def unsent_by_campaigns(campaign_ids: List[str]) -> Dict[str, int]:
	"""Unsent by Campaigns

	Takes a list of campaign IDs and returns the total count per campaign of
	not yet contacted contacts

	Arguments:
		campaign_ids (str[]): The list of `_id`s of campaigns

	Returns:
		A dictionary of counts mapped to IDs
	"""

	# Get the struct
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL
	sSQL = "SELECT `_campaign`, COUNT(`_contact`)\n" \
			"FROM `%(db)s`.`%(table)s`\n" \
			"WHERE `_campaign` in ('%(campaigns)s')" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaigns': '\',\''.join(campaign_ids)
	}

	# Run the search and return the result
	return select(
		sSQL,
		Select.HASH,
		host = dStruct.host
	)

def add_contacts_all(campaign_id: str, project_id: str) -> None:
	"""Add Contacts All

	Adds every single contact in the given project's list

	Arguments:
		campaign_id (str): The ID of the campaign to add the contacts
		project_id (str): The ID of the project to find contacts in

	Returns:
		None
	"""

	# Get the struct
	dStruct = CampaignContact._parent._table._struct

	# Get the contact struct
	dContact = contact.Contact._parent._table._struct

	# Generate the SQL
	sSQL = "INSERT IGNORE INTO `%(db)s`.`%(table)s`" \
			" (`_id`, `_campaign`, `_contact`)\n" \
			"SELECT UUID(), '%(campaign)s', `_id`\n" \
			"FROM `%(cdb)s`.`%(ctable)s`\n" \
			"WHERE `_project` = '%(project)s'\n" \
			"AND `unsubscribed` = 0" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id,
		'cdb': dContact.db,
		'ctable': dContact.name,
		'project': project_id
	}

	# Run the insert and return the number of rows added
	return execute(sSQL, dStruct.host)

def add_contacts_by_categories(
	campaign_id: str, category_ids: List[str]
) -> None:
	"""Add Contacts by Categories

	Adds every single contact found in the given categories' list

	Arguments:
		campaign_id (str): The ID of the campaign to add the contacts
		category_ids (str[]): The IDs of the categories to find contacts in

	Returns:
		None
	"""

	# Get the struct
	dStruct = CampaignContact._parent._table._struct

	# Get the contact structs
	dContact = contact.Contact._parent._table._struct
	dCategories = contact.Contact._parent._complex['categories']._table._struct

	# Generate the SQL
	sSQL = "INSERT IGNORE INTO `%(db)s`.`%(table)s`" \
			" (`_id`, `_campaign`, `_contact`)\n" \
			"SELECT DISTINCT UUID(), '%(campaign)s', `co`.`_id`\n" \
			"FROM `%(contact_db)s`.`%(contact_table)s` as `co`\n" \
			"JOIN `%(categories_db)s`.`%(categories_table)s` as `ca`" \
			" ON `co`.`_id` = `ca`.`_parent`\n" \
			"WHERE `co`.`unsubscribed` = 0\n" \
			"AND `ca`.`_value` IN ('%(categories)s')" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id,
		'contact_db': dContact.db,
		'contact_table': dContact.name,
		'categories_db': dCategories.db,
		'categories_table': dCategories.name,
		'categories': '\',\''.join(category_ids)
	}

	# Run the insert and return the number of rows added
	return execute(sSQL, dStruct.host)

def add_contacts_list(campaign_id: str, contact_ids: List[str]) -> None:
	"""Add Contacts List

	Adds the contacts passed to the given campaign in a single statement

	Arguments:
		campaign_id (str): The ID of the campaign to add the contacts
		contact_ids (str[]): A list of contact IDs to add

	Returns:
		None
	"""

	# Get the struct
	dStruct = CampaignContact._parent._table._struct

	# Generate the insert template
	sValues = "(UUID(), '%s', '%%s')" % campaign_id

	# Generate the SQL
	sSQL = "INSERT IGNORE INTO `%(db)s`.`%(table)s`" \
			" (`_id`, `_campaign`, `_contact`)\n" \
			"VALUES %(rows)s" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'rows': ',\n'.join([ sValues % s for s in contact_ids ])
	}

	# Run the insert and return the number of rows added
	return execute(sSQL, dStruct.host)

def get_with_contact(_id: str) -> dict | None:
	"""Get with Contact

	Fetches the contact info

	Arguments:
		_id (str): The unique ID of the contact in the campaign

	Returns:
		dict | None
	"""

	# Get the structs
	dStruct = CampaignContact._parent._table._struct
	dContact = contact.Contact._parent._table._struct

	# Generate the SQL
	sSQL = "SELECT `cc`.`_contact`, `cc`.`unsubscribed`,\n" \
			"  `c`.`_project`, `c`.`email_address`\n" \
			"FROM `%(db)s`.`%(table)s` as `cc`\n" \
			"LEFT OUTER JOIN `%(contact_db)s`.`%(contact_table)s` as `c`" \
			" ON `cc`.`_contact` = `c`.`_id`\n" \
			"WHERE `cc`.`_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'contact_db': dContact.db,
		'contact_table': dContact.name,
		'_id': escape(_id, host = dStruct.host)
	}

	# Run the statement return the row
	return select(sSQL, Select.ROW, host = dStruct.host)

def next(campaign_id: str) -> dict | Literal[False]:
	"""Next

	Returns the next contact in the campaign that can be delivered

	Arguments:
		campaign_id (str): The ID of the campaign

	Returns:
		dict
	"""

	# Get the struct
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL
	sSQL = "SELECT `_id`, `_contact`\n" \
		 	"FROM `%(db)s`.`%(table)s`\n" \
			"WHERE `_campaign` = '%(campaign)s'\n" \
			"AND `sent` IS NULL\n" \
			"AND `unsubscribed` IS NULL\n" \
			"LIMIT 1" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id
	}

	# Select the statement and return the result
	return select(sSQL, Select.ROW, host = dStruct.host)

def opened(_id: str, contact_id: str = undefined) -> bool:
	"""Opened

	Handles marking the user as opening the email for the specific campaign

	Arguments:
		_id (str): The campaign contact ID

	Returns:
		bool
	"""

	# Get the structs
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL to mark it as such
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `opened` = NOW()\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': escape(_id, host = dStruct.host)
	}

	# Run the SQL and return the result
	return execute(sSQL, host = dStruct.host) and True or False

def sent_and_delivered(_id: str) -> bool:
	"""Sent

	Marks the campaign contact as being sent the message, it most likely was \
	not delivered

	Arguments:
		_id (str): The campaign contact ID

	Returns:
		bool
	"""

	# Get the structs
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL to mark it as such
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `sent` = NOW()\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': escape(_id, host = dStruct.host)
	}

	# Run the SQL and return the result
	return execute(sSQL, host = dStruct.host) and True or False

def sent_and_delivered(_id: str) -> bool:
	"""Sent and Delivered

	Marks the campaign contact as being sent the message, and that it was \
	delivered, at least so far as the SMTP server is concerned

	Arguments:
		_id (str): The campaign contact ID

	Returns:
		bool
	"""

	# Get the structs
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL to mark it as such
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `sent` = NOW(),\n" \
			" `delivered` = NOW()\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': escape(_id, host = dStruct.host)
	}

	# Run the SQL and return the result
	return execute(sSQL, host = dStruct.host) and True or False

def unsubscribe(_id: str, contact_id: str = undefined) -> bool:
	"""Unsubscribe

	Handles marking the user as unsubscribing from the specific campaign as \
	well as any future campaigns for the project

	Arguments:
		_id (str): The campaign contact ID

	Returns:
		bool
	"""

	# Get the structs
	dStruct = CampaignContact._parent._table._struct

	# Generate the SQL to mark it as such
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `unsubscribed` = NOW()\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': escape(_id, host = dStruct.host)
	}

	# If we have didn't get a contact ID
	if contact_id is undefined or contact_id is None:

		# Run the SQL and return the result
		return execute(sSQL, host = dStruct.host) and True or False

	# Generate the contact unsubscribe SQL and make a list of the two
	lSQL = [ sSQL, contact.unsubscribe(contact_id, return_sql = True) ]

	# Execute the statements and return the result
	return execute(lSQL, host = dStruct.host) and True or False