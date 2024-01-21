# coding=utf8
""" Admin Service

Handles all admin / data entry requests
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-07"

# Ouroboros imports
from body import Error, errors, Response, Service
from jobject import jobject
from record.exceptions import RecordDuplicate
from record_mysql import Literal as MySQL_Literal
from tools import evaluate, without
import undefined

# Python imports
from operator import itemgetter

# Import records
from records.admin import \
	campaign, campaign_contact, category, contact, project, sender, \
	unsubscribe

# Import errors
from shared.errors import \
	CONTACT_UNSUBSCRIBED, \
	EMAIL_UNSUBSCRIBED, \
	SENDER_BEING_USED

REPLACE_ME = '00000000-0000-0000-0000-000000000000'

class Admin(Service):
	"""Admin Service class

	Service for authorization, sign in, sign up, permissions etc.

	Extends:
		body.Service
	"""

	def __init__(self):
		"""Admin

		Constructs the object

		Returns:
			Admin
		"""
		pass

	def reset(self):
		"""Reset

		Resets the config

		Returns:
			Admin
		"""
		return self

	def campaign_create(self, req: jobject) -> Response:
		"""Campaign (create)

		Creates a new campaign, paused by default

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check for fields we need to validate outside of the format
		try: evaluate(req.data.record, [
			[ 'record', [
				'_project', '_sender', 'min_interval', 'max_interval'
			] ],
			'contacts'
		])
		except ValueError as e:
			return Error(
				errors.DATA_FIELDS,
				[ [ 'record.%' % s, 'missing' ] for s in e.args ]
			)

		# Make sure the intervals are proper unsigned ints
		lIntErrors = []
		try: req.data.record.min_interval = \
			int(req.data.record.min_interval)
		except ValueError:
			lIntErrors.append([ 'record.max_interval', 'invalid' ])
		try: req.data.record.max_interval = \
			int(req.data.record.max_interval)
		except ValueError:
			lIntErrors.append([ 'record.max_interval', 'invalid' ])
		if lIntErrors: return Error(errors.DATA_FIELDS, )

		# Make sure min is actually less than max
		if req.data.record.min_interval >= req.data.record.max_interval:
			return Error(
				errors.DATA_FIELDS,
				[ 'records.max_interval', 'must be larger than minimum' ]
			)

		# Check the project exists
		if not project.Project.exists(req.data.record._project):
			return Error(
				errors.DB_NO_RECORD,
				[ req.data.record._project, 'project' ]
			)

		# Get the sender
		dSender = sender.Sender.get(
			req.data.record._sender,
			raw = [ '_project' ]
		)
		if not dSender:
			return Error(
				errors.DB_NO_RECORD,
				[ req.data.record._sender, 'sender' ]
			)

		# If the project associated with the sender doesn't match this
		#	campaign's project, we have a problem
		if dSender['_project'] != req.data.record._project:
			return Error(errors.RIGHTS, 'invalid sender for project')

		# If we are adding a list of contacts by ID, or by categories they are
		#	in
		if req.data.contacts in [ 'categories', 'ids' ]:

			# If the list is missing
			if 'contacts_list' not in req.data:
				return Error(
					errors.DATA_FIELDS,
					[ [ 'contacts_list', 'missing' ] ]
				)

			# If we are adding categories
			if req.data.contacts == 'categories':

				# Make absolutely sure the list is unique
				lCategories = list(set(req.data.contacts_list))

				# Make sure they all exist by fetching them all
				lValidCategories = [
					d['_id'] for d in category.Category.filter({
						'_project': req.data.record._project,
						'_id': lCategories
					}, raw = [ '_id' ]
				) ]

				# If the counts don't match
				if len(lValidCategories) != len(lCategories):

					# Get the list of IDs that don't exist and return them in an
					#	error
					return Error(
						errors.DB_NO_RECORD, [
							[ _id for _id in lCategories \
								if _id not in lValidCategories ],
							'category'
						]
					)

			# Else, if we are adding contacts directly
			elif req.data.contacts == 'ids':

				# Make absolutely sure the contacts are unique
				lContacts = list(set(req.data.contacts_list))

				# Make sure they all exist by fetching them all
				lValidContacts = [ d['_id'] for d in contact.Contact.get(
					lContacts, raw = [ '_id' ]
				) ]

				# If the counts don't match
				if len(lValidContacts) != len(lContacts):

					# Get the list of IDs that don't exist and return them in an
					#	error
					return Error(
						errors.DB_NO_RECORD, [
							[ _id for _id in lContacts \
								if _id not in lValidContacts ],
							'contact'
						]
					)

		# Else, we better have received 'all'
		elif req.data.contacts != 'all':
			return Error(
				errors.DATA_FIELDS,
				[ [ 'contacts',
					'must be one of "all", "categories", or "ids"' ] ]
			)

		# If the start now flag is set
		if 'start_now' in req.data and req.data.start_now:
			req.data.record.next_trigger = MySQL_Literal('CURRENT_TIMESTAMP')

		# Create and validate the record
		try:
			sID = campaign.Campaign.add(
				req.data.record,
				revision_info = { 'user': REPLACE_ME }
			)
		except ValueError as e:
			return Error(errors.DATA_FIELDS, e.args)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# If we are adding all the projects contacts
		if req.data.contacts == 'all':
			campaign_contact.add_contacts_all(sID, req.data.record._project)

		# Else, if we are adding contacts by project categories
		elif req.data.contacts == 'categories':
			campaign_contact.add_contacts_by_categories(sID, lCategories)

		# Else, if we are adding by ID
		elif req.data.contacts == 'ids':
			campaign_contact.add_contacts(sID, lContacts)

		# Return the ID
		return Response(sID)

	def categories_read(self, req: jobject) -> Response:
		"""Categories (read)

		Fetches and returns all existing categories in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Get all the records
		lCategories = category.Category.get(raw = True)

		# Sort them by name
		lCategories.sort(key = itemgetter('name'))

		# Find and return the categories
		return Response(lCategories)

	def category_create(self, req: jobject) -> Response:
		"""Category (create)

		Creates a new category in an existing project in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If we are missing the record
		if 'record' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ 'record', 'missing' ] ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Check for project
		if '_project' not in req.data.record:
			return Error(errors.DATA_FIELDS, [ [ '_project', 'missing' ] ])

		# If the project doesn't exist
		if not project.Project.exists(req.data.record._project):
			return Error(
				errors.DB_NO_RECORD,
				[ req.data.record._project, 'project' ]
			)

		# Create and validate the record
		try:
			sID = category.Category.add(
				req.data.record,
				revision_info = { 'user': REPLACE_ME }
			)
		except ValueError as e:
			return Error(errors.DATA_FIELDS, e.args)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Return the result
		return Response(sID)

	def category_delete(self, req: jobject) -> Response:
		"""Category (delete)

		Deletes an existing category from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check the ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# If the category doesn't exist
		if not category.Category.exists(req.data._id):
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'category' ])

		# If there are existing contacts with the category
		lContacts = contact.Contact.filter({
			'categories': req.data._id
		}, raw = [ '_id' ] )
		if lContacts:
			return Error(
				errors.DB_REFERENCES,
				[ req.data.category, 'category', 'in contacts' ]
			)

		# Delete the record
		dRes = category.Category.remove(
			req.data._id,
			revision_info = { 'user': REPLACE_ME }
		)

		# If nothing was deleted
		if dRes == None:
			return Error(errors.DB_DELETE_FAILED, [ req.data._id, 'contact' ])

		# Return OK
		return Response(dRes)

	def category_read(self, req: jobject) -> Response:
		"""Category (read)

		Fetches and returns an existing category

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check for ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Fetch the record
		dCategory = category.Category.get(req.data._id, raw = True)
		if not dCategory:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'category' ])

		# Return the record
		return Response(dCategory)

	def category_update(self, req: jobject) -> Response:
		"""Category (update)

		Updates an existing category

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ '_id', 'record' ])
		except ValueError as e:
			return Error(
				errors.DATA_FIELDS, [ [ k, 'missing' ] for k in e.args ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Find the category
		oCategory = category.Category.get(req.data._id)
		if not oCategory:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'category' ])

		# Remove any fields found that can't be altered by the user
		without(
			req.data.record,
			[ '_id', '_created', '_updated', '_project' ],
			True
		)

		# Update it using the record data sent
		try:
			dChanges = oCategory.update(req.data.record)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Test if the updates are valid
		if not oCategory.valid():
			return Error(errors.DATA_FIELDS, oCategory.errors)

		# Save the record and store the result
		bRes = oCategory.save(revision_info = { 'user' : REPLACE_ME })

		# Return the changes or False
		return Response(bRes and dChanges or False)

	def contact_create(self, req: jobject) -> Response:
		"""Contact (create)

		Creates a new contact in an existing project in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If we are missing the record
		if 'record' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ 'record', 'missing' ] ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Check for project
		if '_project' not in req.data.record:
			return Error(errors.DATA_FIELDS, [ [ '_project', 'missing' ] ])

		# If the project doesn't exist
		if not project.Project.exists(req.data.record._project):
			return Error(
				errors.DB_NO_RECORD,
				[ req.data.record._project, 'project' ]
			)

		# If the email is missing
		if 'email_address' not in req.data.record:
			return Error(errors.DATA_FIELDS, [ [ 'email_address', 'missing' ] ])

		# Look for the email in the unsubscribe list for the same project
		dUnsubscribe = unsubscribe.Unsubscribe.filter({
			'_project': req.data.record._project,
			'email_address': req.data.record.email_address
		}, raw = [ '_id' ])
		if dUnsubscribe:
			return Error(EMAIL_UNSUBSCRIBED, [
				req.data.record._project,
				req.data.record.email_address
			])

		# Create and validate the record
		try:
			sID = contact.Contact.add(
				req.data.record,
				revision_info = { 'user': REPLACE_ME }
			)
		except ValueError as e:
			return Error(errors.DATA_FIELDS, e.args)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Return the result
		return Response(sID)

	def contact_delete(self, req: jobject) -> Response:
		"""Contact (delete)

		Deletes an existing contact from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check the ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# If the contact doesn't exist
		if not contact.Contact.exists(req.data._id):
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'contact' ])

		# Delete the record
		dRes = contact.Contact.remove(
			req.data._id,
			revision_info = { 'user': REPLACE_ME }
		)

		# If nothing was deleted
		if dRes == None:
			return Error(errors.DB_DELETE_FAILED, [ req.data._id, 'contact' ])

		# Return OK
		return Response(dRes)

	def contact_read(self, req: jobject) -> Response:
		"""Contact (read)

		Fetches and returns an existing contact

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check for ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Fetch the record
		dContact = contact.Contact.get(req.data._id, raw = True)
		if not dContact:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'contact' ])

		# Return the record
		return Response(dContact)

	def contact_update(self, req: jobject) -> Response:
		"""Contact (update)

		Updates an existing contact

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ '_id', 'record' ])
		except ValueError as e:
			return Error(
				errors.DATA_FIELDS, [ [ k, 'missing' ] for k in e.args ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Find the contact
		oContact = contact.Contact.get(req.data._id)
		if not oContact:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'contact' ])

		# If the contact is unsubscribed, don't allow any updates
		if oContact['unsubscribed']:
			return Error(CONTACT_UNSUBSCRIBED, req.data._id)

		# If we have categories
		if 'categories' in req.data.record:

			# Make sure all the categories exist
			if not category.Category.exists(req.data.record.categories):
				return Error(
					errors.DB_NO_RECORD,
					[ req.data.record.categories, 'category' ]
				)

		# Remove any fields found that can't be altered by the user
		without(
			req.data.record,
			[ '_id', '_created', '_updated', '_project', 'unsubscribed' ],
			True
		)

		# Update it using the record data sent
		try:
			dChanges = oContact.update(req.data.record)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Test if the updates are valid
		if not oContact.valid():
			return Error(errors.DATA_FIELDS, oContact.errors)

		# Save the record and store the result
		bRes = oContact.save(revision_info = { 'user' : REPLACE_ME })

		# Return the changes or False
		return Response(bRes and dChanges or False)

	def contacts_read(self, req: jobject) -> Response:
		"""Contacts (read)

		Fetches contacts by project and optionally by category

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If the project is not passed
		if '_project' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_project', 'missing' ] ])

		# Init the search filter
		dFilter = { '_project': req.data._project }

		# If we have categories
		if 'categories' in req.data:
			dFilter['categories'] = req.data.categories

		# Request the contacts
		lContacts = contact.Contact.filter(dFilter, raw = True)

		# Sort them by name
		lContacts.sort(key = itemgetter('name'))

		# Return the records
		return Response(lContacts)

	def project_create(self, req: jobject) -> Response:
		"""Project (create)

		Creates a new project in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If we are missing the record
		if 'record' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ 'record', 'missing' ] ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Make sure the short code is all uppercase
		if 'short_code' in req.data.record:
			req.data.record.short_code = req.data.record.short_code.upper()

		# Create and validate the record
		try:
			sID = project.Project.add(
				req.data.record,
				revision_info = { 'user': REPLACE_ME }
			)
		except ValueError as e:
			return Error(errors.DATA_FIELDS, e.args)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Return the result
		return Response(sID)

	def project_delete(self, req: jobject) -> Response:
		"""Project (delete)

		Deletes an existing project from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the project
		oProject = project.Project.get(req.data._id)
		if not oProject:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'project' ])

		# Delete the record
		if oProject.remove(revision_info = { 'user': REPLACE_ME }) == 0:
			return Error(errors.DB_DELETE_FAILED, [ req.data._id, 'project' ])

		# Return OK
		return Response(True)

	def project_read(self, req: jobject) -> Response:
		"""Project (read)

		Fetches and returns an existing project from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If we got an ID
		if '_id' in req.data:
			mIndex = undefined
			_id = req.data._id

		# Else, if we got a short code
		elif 'short_code' in req.data:
			mIndex = 'ui_short_code'
			_id = req.data.short_code

		# Else, missing an ID
		else:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the project
		dProject = project.Project.get(_id, index = mIndex, raw = True)
		if not dProject:
			return Error(errors.DB_NO_RECORD, [ _id, 'project' ])

		# Return the record
		return Response(dProject)

	def project_update(self, req: jobject) -> Response:
		"""Project (update)

		Updates an existing project in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ '_id', 'record' ])
		except ValueError as e:
			return Error(
				errors.DATA_FIELDS, [ [ k, 'missing' ] for k in e.args ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Find the project
		oProject = project.Project.get(req.data._id)
		if not oProject:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'project' ])

		# Remove any fields found that can't be altered by the user
		without(
			req.data.record,
			[ '_id', '_created', '_updated', 'short_code' ],
			True
		)

		# Update it using the record data sent
		try:
			dChanges = oProject.update(req.data.record)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Test if the updates are valid
		if not oProject.valid():
			return Error(errors.DATA_FIELDS, oProject.errors)

		# Save the record and store the result
		bRes = oProject.save(revision_info = { 'user' : REPLACE_ME })

		# Return the changes or False
		return Response(bRes and dChanges or False)

	def projects_read(self, req: jobject) -> Response:
		"""Projects (read)

		Fetches and returns all existing projects in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Get all the records
		lProjects = project.Project.get(raw = True)

		# Sort them by name
		lProjects.sort(key = itemgetter('name'))

		# Find and return the projects
		return Response(lProjects)

	def sender_create(self, req: jobject) -> Response:
		"""Sender (create)

		Creates a new sender in an existing project in the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If we are missing the record
		if 'record' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ 'record', 'missing' ] ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Check for project
		if '_project' not in req.data.record:
			return Error(errors.DATA_FIELDS, [ [ '_project', 'missing' ] ])

		# If the project doesn't exist
		if not project.Project.exists(req.data.record._project):
			return Error(
				errors.DB_NO_RECORD,
				[ req.data.record._project, 'project' ]
			)

		# If TLS not set, assume False
		if 'tls' not in req.data.record:
			req.data.record.tls = False

		# Create and validate the record
		try:
			sID = sender.Sender.add(
				req.data.record,
				revision_info = { 'user': REPLACE_ME }
			)
		except ValueError as e:
			return Error(errors.DATA_FIELDS, e.args)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Return the result
		return Response(sID)

	def sender_delete(self, req: jobject) -> Response:
		"""Sender (delete)

		Deletes an existing sender from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check the ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# If the sender doesn't exist
		if not sender.Sender.exists(req.data._id):
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'sender' ])

		# Look for campaigns with the sender
		lCampaigns = campaign.Campaign.filter({
			'_sender': req.data._id
		}, raw = [ '_id' ])

		# If there's any campaigns
		if lCampaigns:

			# Look for any campaign contacts still not sent
			dCampaignContacts = campaign_contact.unsent_by_campaigns(
				[ d['_id'] for d in lCampaigns ]
			)

			# If there's any
			if dCampaignContacts:
				return Error(SENDER_BEING_USED, dCampaignContacts)

		# Delete the record
		dRes = sender.Sender.remove(
			req.data._id,
			revision_info = { 'user': REPLACE_ME }
		)

		# If nothing was deleted
		if dRes == None:
			return Error(errors.DB_DELETE_FAILED, [ req.data._id, 'sender' ])

		# Return OK
		return Response(dRes)

	def sender_read(self, req: jobject) -> Response:
		"""Sender (read)

		Fetches and returns an existing sender

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check for ID
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Fetch the record
		dSender = sender.Sender.get(req.data._id, raw = True)
		if not dSender:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'sender' ])

		# Strip out the password
		del dSender['password']

		# Return the record
		return Response(dSender)

	def sender_update(self, req: jobject) -> Response:
		"""Sender (update)

		Updates an existing sender

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ '_id', 'record' ])
		except ValueError as e:
			return Error(
				errors.DATA_FIELDS, [ [ k, 'missing' ] for k in e.args ])

		# If the record is not a dict
		if not isinstance(req.data.record, dict):
			return Error(errors.DATA_FIELDS, [ [ 'record', 'invalid' ] ])

		# Find the sender
		oSender = sender.Sender.get(req.data._id)
		if not oSender:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'sender' ])

		# Remove any fields found that can't be altered by the user
		without(
			req.data.record,
			[ '_id', '_created', '_updated', '_project' ],
			True
		)

		# Update it using the record data sent
		try:
			dChanges = oSender.update(req.data.record)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Test if the updates are valid
		if not oSender.valid():
			return Error(errors.DATA_FIELDS, oSender.errors)

		# Save the record and store the result
		bRes = oSender.save(revision_info = { 'user' : REPLACE_ME })

		# Return the changes or False
		return Response(bRes and dChanges or False)

	def senders_read(self, req: jobject) -> Response:
		"""Senders (read)

		Fetches senders by project

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If the project is not passed
		if '_project' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_project', 'missing' ] ])

		# Request the senders
		lSenders = sender.Sender.filter({
			'_project': req.data._project
		}, raw = True)

		# Sort them by email
		lSenders.sort(key = itemgetter('email_address'))

		# Try to remove all passwords
		for d in lSenders:
			try: del d['password']
			except: pass

		# Return the records
		return Response(lSenders)