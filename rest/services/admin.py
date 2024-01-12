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
from tools import evaluate, without
import undefined

# Import records
from records.admin import category, contact, project, unsubscribe

# Import errors
from shared.errors import EMAIL_UNSUBSCRIBED

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
			['_id', '_created', '_updated', '_project'],
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
			['_id', '_created', '_updated', '_project'],
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
			['_id', '_created', '_updated', 'short_code'],
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