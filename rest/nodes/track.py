# coding=utf8
""" Track service

Handles tracking if the user opened the email or not
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-02-05"

# Ouroboros imports
from config import config
import record_mysql

# Pip imports
import bottle

# Record imports
from records.contact import campaign_contact

# Constants
with open('templates/track/1x1.png', 'rb') as f:
	rsPixel = f.read()

class Track(bottle.Bottle):
	"""Track

	Used to handle track requests

	Extends:
		Bottle
	"""

	def __init__(self):
		"""Constructor

		Creates a new Track instance

		Returns:
			Track
		"""

		# Call the parent constructor first so the object is setup
		super(Track, self).__init__()

		# Add the routes
		self.route('/<_id>', 'GET', getattr(self, 'index_get'))

	def index_get(self, _id: str):
		"""Index (GET)

		Marks the user as opening the campaign

		Arguments:
			_id (str): The ID of the contact in the campaign
			email_address (str): The email address the user wants to unsubscribe

		Returns:
			Response
		"""

		# Set the return to HTML
		bottle.response.headers['Content-Type'] = 'image/png'

		# Mark the contact as opened
		campaign_contact.opened(_id)

		# Return the response
		return rsPixel

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
	dConf = config.track({
		'host': '0.0.0.0',
		'port': 9101,
		'workers': 1,
		'timeout': 30
	})

	# Run the webserver
	Track().run(
		host = dConf['host'],
		port = dConf['port'],
		server = 'gunicorn',
		workers = dConf['workers'],
		timeout = dConf['timeout']
	)