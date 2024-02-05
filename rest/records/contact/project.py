# coding=utf8
""" Admin Project Record

Handles the project record structure
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-07"

# Ouroboros imports
from config import config
import jsonb
from record_mysql import Storage
import record_redis # to enable redis cache

# Python imports
from pathlib import Path

# Create the Storage instance
Project = Storage(

	# The primary definition
	jsonb.load(
		'%s/definitions/admin/project.json' % \
			Path(__file__).parent.parent.parent.resolve()
	),

	# The extensions necessary to store the data and revisions in MySQL
	{
		# Cache related
		'__cache__': {
			'implementation': 'redis',
			'redis': config.records.cache({
				'name': 'records',
				'ttl': 0
			}),
			'indexes': { 'ui_short_code': 'short_code' }
		},

		# Table related
		'__mysql__': {
			'charset': 'utf8mb4',
			'collate': 'utf8mb4_unicode_ci',
			'create': [
				'_created', '_updated', 'name', 'short_code', 'description'
			],
			'db': config.mysql.db('contact'),
			'indexes': {
				'ui_name' : {
					'fields': 'name',
					'type': 'unique'
				},
				'ui_short_code' : {
					'fields': 'short_code',
					'type': 'unique'
				}
			},
			'name': 'admin_project',
			'revisions': [ 'user' ]
		},

		# Field related
		'_created': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP'
		} },
		'_updated': { '__mysql__': {
			'opts': 'not null default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP'
		} },
		'short_code': { '__mysql__': { 'type': 'char(4)' } }
	}
)