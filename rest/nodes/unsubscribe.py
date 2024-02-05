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
import record_mysql

# Pip imports
import bottle
from jinja2 import FileSystemLoader, Environment, select_autoescape

# Record imports
from records.admin import campaign_contact, project

# Templates
tpl = { 'index': None, 'response': None }

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
		self.route('/<_id>', 'GET', getattr(self, 'index_get'))
		self.route('/<_id>', 'POST', getattr(self, 'index_post'))
		self.route('/oneclick/<_id>', 'GET', getattr(self, 'one_click'))

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

	def index_get(self, _id: str):
		"""Index (GET)

		Asks the user to confirm unsubscribing from the project

		Arguments:
			_id (str): The ID of the contact in the campaign
			email_address (str): The email address the user wants to unsubscribe

		Returns:
			Response
		"""

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = \
				'text/html; charset=utf-8'

		# Find the campaign contact with the contact info
		dContact = campaign_contact.get_with_contact(_id)

		# If there's no such campaign contact, just return
		if not dContact or dContact['unsubscribed']:
			return self._response.render(error = 'no_contact')

		# Find the project and set the name
		dProject = project.Project.get(dContact['_project'], raw = [ 'name' ])
		if not dProject:
			return self._index.render(error = 'no_project')

		# Render the template
		sHTML = self._index.render(info = {
			'project_name': dProject['name'],
			'email_address': dContact['email_address']
		})

		# Set content length and return response
		bottle.response.headers['Content-Length'] = len(sHTML)
		return bottle.Response(sHTML, 200)

	def index_post(self, _id: str) -> str:
		"""Index (POST)

		Handles the confirmation of unsubscribe

		Arguments:
			short_code (str): The short code for the project
			email_address (str): The email address the user wants to unsubscribe

		Returns:
			Response
		"""

		# Call the one click method and return the result
		return self.one_click(_id)

	def one_click(self, _id: str):
		"""One Click

		Passed in the header of emails in order to allow users to instantly \
		unsubscribe from the system

		Arguments:
			_id (str): The unique ID of the contact in the campaign

		Returns:
			Response
		"""

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = \
				'text/html; charset=utf-8'

		# Find the campaign contact with the contact info
		dContact = campaign_contact.get_with_contact(_id)

		# If there's no such campaign contact, just return
		if not dContact:
			return self._response.render(error = 'no_contact')

		# If the contact is already unsubscribed
		if dContact['unsubscribed']:
			return self._response.render(error = 'no_contact')

		# Mark the contact as unsubscribed
		if not campaign_contact.unsubscribe(_id, dContact['_contact']):
			return self._response.render(error = 'unsubscribe')

		# Find the project and set the name
		dProject = project.Project.get(dContact['_project'], raw = [ 'name' ])
		sProjectName = dProject and dProject['name'] or 'PROJECT NOT FOUND'

		# Generate HTML
		sHTML = self._response.render(
			email_address = dContact['email_address'],
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