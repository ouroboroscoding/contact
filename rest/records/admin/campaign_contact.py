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
from record_mysql.server import execute, select, Select

# Python imports
from pathlib import Path
from typing import Dict, List, Literal

# Other records
from records.admin.contact import Contact

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
				'_campaign', '_contact', 'sent', 'delivered', 'opened'
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

	# DEBUGGING
	print(sSQL)

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
	dContact = Contact._parent._table._struct

	# Generate the SQL
	sSQL = "INSERT IGNORE INTO `%(db)s`.`%(table)s`" \
			" (`_id`, `_campaign`, `_contact`)\n" \
			"SELECT UUID(), '%(campaign)s', `_id`\n" \
			"FROM `%(cdb)s`.`%(ctable)s`\n" \
			"WHERE `_project` = '%(project)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id,
		'cdb': dContact.db,
		'ctable': dContact.name,
		'project': project_id
	}

	print(sSQL)

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

	# Get the contact categories struct
	dCategories = Contact._parent._complex['categories']._table._struct

	# Generate the SQL
	sSQL = "INSERT IGNORE INTO `%(db)s`.`%(table)s`" \
			" (`_id`, `_campaign`, `_contact`)\n" \
			"SELECT DISTINCT UUID(), '%(campaign)s', `_parent`\n" \
			"FROM `%(cdb)s`.`%(ctable)s`\n" \
			"WHERE `_value` IN ('%(categories)s')" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id,
		'cdb': dCategories.db,
		'ctable': dCategories.name,
		'categories': '\',\''.join(category_ids)
	}

	print(sSQL)

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

	print(sSQL)

	# Run the insert and return the number of rows added
	return execute(sSQL, dStruct.host)

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
			"AND `sent` = 0\n" \
			"LIMIT 1" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'campaign': campaign_id
	}

	print(sSQL)

	# Select the statement and return the result
	return select(sSQL, Select.ROW, host = dStruct.host)