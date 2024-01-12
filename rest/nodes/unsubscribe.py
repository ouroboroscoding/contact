# coding=utf8
""" Unsubscribe service

Handles users unsubscribing from the system
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-08-25"

# Ouroboros imports
from config import config
from record.exceptions import RecordDuplicate, RecordServerException
import record_mysql

# Pip imports
import bottle
from jinja2 import FileSystemLoader, Environment, select_autoescape

# Record imports
from records.admin import contact, project, unsubscribe

# Templates
tpl = {
	'index': None,
	'response': None
}

class Unsubscribe(bottle.Bottle):
	"""Unsubscribe

	Used to handle unsubscribe requests

	Extends:
		Bottle
	"""

	def __init__(self):
		"""Constructor

		Creates a new Unsubscribe instance

		Returns:
			Unsubscribe
		"""

		# Call the parent constructor first so the object is setup
		super(Unsubscribe, self).__init__()

		# Add the routes
		self.route('/<short_code:re:[A-Z]{3,4}>/<email_address>', 'GET', getattr(self, 'index_get'))
		self.route('/<short_code:re:[A-Z]{3,4}>/<email_address>', 'POST', getattr(self, 'index_post'))
		self.route('/oneclick/<id>', 'GET', getattr(self, 'one_click'))

		# Init Jinja and load templates
		jinja = Environment(
			loader = FileSystemLoader('templates/unsubscribe'),
			autoescape = select_autoescape(
				enabled_extensions = ('html'),
				default_for_string = True
			)
		)
		self._index = jinja.get_template('index.html.jinja')
		self._response = jinja.get_template('response.html.jinja')

	def index_get(self, short_code: str, email_address: str):
		"""Index (GET)

		Asks the user to confirm unsubscribing from the project

		Arguments:
			short_code (str): The short code for the project
			email_address (str): The email address the user wants to unsubscribe

		Returns:
			Response
		"""

		print('index GET called')

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = \
				'text/html; charset=utf-8'

		# Find the project by short code
		dProject = project.Project.get(
			short_code,
			index = 'ui_short_code',
			raw = [ 'name' ]
		)

		# If the project doesn't exist
		if not dProject:
			return self._index.render(error = 'no_project')

		# Rendeer the template
		sHTML = self._index.render(info = {
			'project_name': dProject['name'],
			'email_address': email_address
		})

		# Set content length and return response
		bottle.response.headers['Content-Length'] = len(sHTML)
		return bottle.Response(sHTML, 200)

	def index_post(self, short_code: str, email_address: str):
		"""Index (POST)

		Handles the confirmation of unsubscribe

		Arguments:
			short_code (str): The short code for the project
			email_address (str): The email address the user wants to unsubscribe

		Returns:
			Response
		"""

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = \
				'text/html; charset=utf-8'

		# Find the project by short code
		dProject = project.Project.get(
			short_code,
			index = 'ui_short_code',
			raw = [ '_id', 'name' ]
		)

		# If the project doesn't exist
		if not dProject:
			return self._response.render(error = 'no_project')

		# Store the project name
		sProjectName = dProject['name']

		# Find the contact by project and email
		oContact = contact.Contact.get((
			dProject['_id'], email_address
		), index = 'ui_project_email')

		# If there's no such contact
		if not oContact:
			return self._response.render(error = 'no_contact')

		# Add the contact to the unsubscribed list using the same project and
		#	email address
		try:
			unsubscribe.Unsubscribe.add({
				'_project': dProject['_id'],
				'email_address': email_address
			}, revision_info = { 'user': 'oneclick' })

		# If there was a failure
		except RecordServerException:
			return self._response.render(
				error = 'unsubscribe',
				email_address = email_address
			)

		# If the email is already unsubscribed, do nothing
		except RecordDuplicate:
			pass

		# Delete the contact so it can't be used anymore
		try:
			oContact.remove(revision_info = { 'user': 'unsubscribe_confirm' })
		except Exception:
			pass

		# Generate the HTML
		sHTML = self._response.render(
			email_address = email_address,
			project_name = sProjectName
		)

		# Set content length and return response
		bottle.response.headers['Content-Length'] = len(sHTML)
		return bottle.Response(sHTML, 200)

	def one_click(self, id: str):
		"""One Click

		Passed in the header of emails in order to allow users to instantly \
		unsubscribe from the system

		Arguments:
			id (str): The unique ID of the user wishing to unsubscribe

		Returns:
			Response
		"""

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = \
				'text/html; charset=utf-8'

		print('one_click GET called')

		# Find the contact
		oContact = contact.Contact.get(id)

		# If there's no such contact, just return
		if not oContact:
			return self._response.render(error = 'no_contact')

		# Set the project ID and email
		sProjectID = oContact['_project']
		sEmailAddress = oContact['email_address']

		# Add the contact to the unsubscribed list using the same project and
		#	email address
		try:
			unsubscribe.Unsubscribe.add({
				'_project': sProjectID,
				'email_address': sEmailAddress
			}, revision_info = { 'user': 'oneclick' })

		# If there was a failure
		except RecordServerException:
			return self._response.render(
				error = 'unsubscribe',
				email_address = sEmailAddress
			)

		# If the email is already unsubscribed, do nothing
		except RecordDuplicate:
			pass

		# Delete the contact so it can't be used anymore
		try:
			oContact.remove(revision_info = { 'user': 'unsubscribe_oneclick' })
		except Exception:
			pass

		# Find the project and set the name
		dProject = project.Project.get(sProjectID, raw = [ 'name' ])
		sProjectName = dProject and dProject['name'] or 'PROJECT NOT FOUND'

		# Generate HTML
		sHTML = self._response.render(
			email_address = sEmailAddress,
			project_name = sProjectName
		)

		# Set content length and return response
		bottle.response.headers['Content-Length'] = len(sHTML)
		return bottle.Response(sHTML, 200)

	# run method
	def run(self, server='gunicorn', host='127.0.0.1', port=8080,
			reloader=False, interval=1, quiet=False, plugins=None,
			debug=None, maxfile=20971520, **kargs):
		"""Run

		Overrides Bottle's run to default gunicorn and other fields

		Arguments:
			server (str): Server adapter to use
			host (str): Server address to bind to
			port (int): Server port to bind to
			reloader (bool): Start auto-reloading server?
			interval (int): Auto-reloader interval in seconds
			quiet (bool): Suppress output to stdout and stderr?
			plugins (list): List of plugins to the server
			debug (bool): Debug mode
			maxfile (int): Maximum size of requests

		Returns:
			None
		"""

		# Set the max file size
		bottle.BaseRequest.MEMFILE_MAX = maxfile

		# Call bottle run
		bottle.run(
			app=self, server=server, host=host, port=port, reloader=reloader,
			interval=interval, quiet=quiet, plugins=plugins, debug=debug,
			**kargs
		)

# Only run if called directly
if __name__ == "__main__":

	# Add the primary host
	record_mysql.add_host(config.mysql.primary({
		'charset': 'utf8',
		'host': 'localhost',
		'passwd': '',
		'port': 3306,
		'user': 'mysql'
	}))

	# Get config
	dConf = config.unsubscribe({
		'host': '0.0.0.0',
		'port': 9100,
		'workers': 1,
		'timeout': 30
	})

	# Run the webserver
	Unsubscribe().run(
		host = dConf['host'],
		port = dConf['port'],
		server = 'gunicorn',
		workers = dConf['workers'],
		timeout = dConf['timeout']
	)