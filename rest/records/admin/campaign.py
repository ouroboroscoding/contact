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

# Python imports
from pathlib import Path

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
				'next_trigger', 'minimum_interval', 'maximum_interval',
				'subject', 'content'
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