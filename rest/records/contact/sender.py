# coding=utf8
""" Sender Record

Handles the sender record structure
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
Sender = Storage(

	# The primary definition
	jsonb.load(
		'%s/definitions/contact/sender.json' % \
			Path(__file__).parent.parent.parent.resolve()
	),

	# The extensions necessary to store the data and revisions in MySQL
	{
		# Table related
		'__mysql__': {
			'charset': 'utf8mb4',
			'collate': 'utf8mb4_unicode_ci',
			'create': [
				'_created', '_updated', '_project', 'email_address', 'password',
				'host', 'port', 'tls'
			],
			'db': config.mysql.db('contact'),
			'indexes': {
				'i_project': '_project',
				'ui_project_email': {
					'fields': [ '_project', 'email_address' ],
					'type': 'unique'
				}
			},
			'name': 'contact_sender',
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