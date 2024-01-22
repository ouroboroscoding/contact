# coding=utf8
""" Admin Campaign Record

Handles the campaign record structure
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
from record_mysql.server import execute

# Python imports
from pathlib import Path
from random import uniform
from typing import List

# Create the Storage instance
Campaign = Storage(

	# The primary definition
	jsonb.load(
		'%s/definitions/admin/campaign.json' % \
			Path(__file__).parent.parent.parent.resolve()
	),

	# The extensions necessary to store the data and revisions in MySQL
	{
		# Table related
		'__mysql__': {
			'charset': 'utf8mb4',
			'collate': 'utf8mb4_unicode_ci',
			'create': [
				'_created', '_updated', '_project', '_sender', 'name',
				'next_trigger', 'min_interval', 'max_interval',	'subject',
				'content'
			],
			'db': config.mysql.db('contact'),
			'indexes': {
				'i_project': '_project',
				'i_next_trigger': 'next_trigger'
			},
			'name': 'admin_campaign',
			'revisions': [ 'user' ]
		},

		# Field related
		'_created': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP'
		} },
		'_updated': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP'
		} }
	}
)

def pause(campaign_id: str) -> bool:
	"""Pause

	Pauses an existing campaign

	Arguments:
		campaign_id (str): The ID of the campaign to pause

	Returns:
		bool
	"""

	# Get the struct
	dStruct = Campaign._parent._table._struct

	# Generate the SQL
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `next_trigger` = NULL\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': campaign_id
	}

	print(sSQL)

	# Run the statement
	return execute(sSQL, dStruct.host) and True or False

def set_next(campaign_id: str, minmax: List[int]) -> bool:
	"""Pause

	Pauses an existing campaign

	Arguments:
		campaign_id (str): The ID of the campaign to pause

	Returns:
		bool
	"""

	# Get the struct
	dStruct = Campaign._parent._table._struct

	# Get a random value between the min and max
	iInterval = uniform(minmax[0], minmax[1])

	# Generate the SQL
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `next_trigger` = DATE_ADD(NOW(), INTERVAL %(interval)s second)\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'interval': str(iInterval),
		'_id': campaign_id
	}

	print(sSQL)

	# Run the statement
	return execute(sSQL, dStruct.host) and True or False