# coding=utf8
"""Campaigns

Handles sending off messages for campaigns
"""

__author__		= "Chris Nasr"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-21"

# Ouroboros imports
from config import config
import record_mysql

# Python imports
from time import sleep, time

# Pip imports
import arrow

# Record imports
from records.admin import campaign, campaign_contact, contact, sender

# Only run if called directly
if __name__ == '__main__':

	# Add the primary host
	record_mysql.add_host(config.mysql.primary({
		'charset': 'utf8',
		'host': 'localhost',
		'passwd': '',
		'port': 3306,
		'user': 'mysql'
	}))

	# Fetch any campaigns that are at or past their trigger
	lCampaigns = campaign.Campaign.filter(
		{ 'next_trigger': { 'lte': arrow.get().timestamp } },
		raw = [ '_id', '_sender', 'min_interval', 'max_interval', 'subject',
				'content' ]
	)

	# If there's none, wait for 30 seconds
	if not lCampaigns:
		sleep(30)

	# Go through each one
	for dCampaign in lCampaigns:

		# Get the sender
		dSender = sender.Sender.get(dCampaign['_sender'], raw = True)

		# If the sender does not exist, pause the campaign
		if not dSender:
			campaign.pause(dCampaign['_id'])
			continue

		# Get the next campaign contact
		dCampaignContact = campaign_contact.next(dCampaign['_id'])

		# If there's none, pause the campaign
		if not dCampaignContact:
			campaign.pause(dCampaign['_id'])
			continue

		# Find the contacts details
		dContact = contact.Contact.get(dCampaignContact['_contact'])

		# If they don't exist, pause the campaign
		if not dContact:
			campaign.pause(dCampaign['_id'])
			continue

		# Generate the template using the contacts details