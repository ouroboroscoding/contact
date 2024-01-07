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

# Import records
from records.admin import project

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
		oProject = project.Project.fetch(req.data._id)
		if not oProject:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'project' ])

		# Delete the record
		mRes = oProject.remove(revision_info = { 'user': REPLACE_ME })

		# Return the result
		return Response(mRes)

	def project_read(self, req: jobject) -> Response:
		"""Project (read)

		Fetches and returns an existing project from the system

		Arguments:
			req (jobject): Contains data and session if available

		Returns:
			Services.Response
		"""

		# If the ID is missing
		if '_id' not in req.data:
			return Error(errors.DATA_FIELDS, [ [ '_id', 'missing' ] ])

		# Find the project
		dProject = project.Project.fetch(req.data._id, raw = True)
		if not dProject:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'project' ])

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
		oProject = project.Project.fetch(req.data._id)
		if not oProject:
			return Error(errors.DB_NO_RECORD, [ req.data._id, 'project' ])

		# Remove any fields found that can't be altered by the user
		without(req.data.record, ['_id', '_created', '_updated'], True)

		# Update it using the record data sent
		try:
			dChanges = oProject.update(req.data.record)
		except RecordDuplicate as e:
			return Error(errors.DB_DUPLICATE, e.args)

		# Test if the updates are valid
		if not oProject.valid():
			return Error(errors.DATA_FIELDS, oProject.errors)

		# Save the user and store the result
		bRes = oProject.save(revision_info = { 'user' : req.session.user })

		# Return the changes or False
		return Response(bRes and dChanges or False)