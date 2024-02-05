# coding=utf8
""" Admin Contact Record

Handles the contact record structure
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-11"

# Ouroboros imports
from config import config
import jsonb
from record_mysql import Storage
from record_mysql.server import escape, execute

# Python imports
from pathlib import Path

# Create the Storage instance
Contact = Storage(

	# The primary definition
	jsonb.load(
		'%s/definitions/admin/contact.json' % \
			Path(__file__).parent.parent.parent.resolve()
	),

	# The extensions necessary to store the data and revisions in MySQL
	{
		# Table related
		'__mysql__': {
			'charset': 'utf8mb4',
			'collate': 'utf8mb4_unicode_ci',
			'create': [
				'_created', '_updated', '_project', 'unsubscribed',
				'email_address', 'name', 'alias', 'company'
			],
			'db': config.mysql.db('contact'),
			'indexes': {
				'ui_project_email': {
					'fields': [ '_project', 'email_address' ],
					'type': 'unique'
				},
				'i_project': '_project'
			},
			'name': 'admin_contact',
			'revisions': [ 'user' ]
		},

		# Field related
		'_created': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP'
		} },
		'_updated': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP'
		} },
		'unsubscribed': { '__mysql__': {
			'opts': 'not null default 0'
		} },

		# Extended related
		'categories': {

			# Table related
			'__mysql__': {
				'indexes': {
					'ui_value_parent': {
						'fields': [ '_value', '_parent' ],
						'type': 'unique'
					}
				}
			}
		}
	}
)

def unsubscribe(_id: str, return_sql: bool = False) -> bool | str:
	"""Unsubscribe

	Marks the given contact as unsubscribed so it can't be used again. If the \
	return_sql flag is set to True, returns the SQL so it can be run with \
	other statements instead of running it directly

	Arguments:
		_id (str): The unique ID of the contact
		return_sql (bool): Optional, if set to true, returns the generated \
			sql instead of running it

	Returns:
		boolean if statement is run, else returns the statement itself
	"""

	# Get the struct
	dStruct = Contact._parent._table._struct

	# Generate the SQL
	sSQL = "UPDATE `%(db)s`.`%(table)s` SET\n" \
			" `unsubscribed` = 1\n" \
			"WHERE `_id` = '%(_id)s'" % {
		'db': dStruct.db,
		'table': dStruct.name,
		'_id': escape(_id, host = dStruct.host)
	}

	print(sSQL)

	# If we want to return the SQL
	if return_sql:
		return sSQL

	# Else, run the statement and return the result
	return execute(sSQL, host = dStruct.host) and True or False