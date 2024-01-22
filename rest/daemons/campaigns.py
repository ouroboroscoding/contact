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
from strings import strtr

# Python imports
from time import sleep, time

# Pip imports
import arrow

# Record imports
from records.admin import \
	campaign, campaign_contact, contact, sender, unsubscribe

def get_next_contact(campaign_id: str) -> dict | None:
	"""Get Next Contact

	Finds the next usable contact in a campaign, or None if there are none
	left

	Arguments:
		campaign_id (str): The unique ID of the campaign

	Returns:
		dict | None
	"""

	# Loop until we get a contact, or there are no more
	while True:

		# Get the next campaign contact
		dCampaignContact = campaign_contact.next(campaign_id)

		# If there is none, return immediately
		if not dCampaignContact:
			return None

		# Find the contacts details
		dContact = contact.Contact.get(dCampaignContact['_contact'])

		# If they don't exist, remove them and start again
		if not dContact:
			campaign_contact.CampaignContact.remove(dCampaignContact['_id'])
			continue

		# If the contact is unsubscribed, remove them and start again
		if dContact['unsubscribed']:
			campaign_contact.CampaignContact.remove(dCampaignContact['_id'])
			continue

		# Make absolutely sure
		if unsubscribe.Unsubscribe.exists(
			(dCampaign['_project'], dContact['email_address']),
			'ui_project_email'
		):
			campaign_contact.CampaignContact.remove(dCampaignContact['_id'])
			continue

		# Add the campaign contact ID to the data
		dContact['campaign_contact_id'] = dCampaignContact['_id']

		# Return the contact
		return dContact


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

		# Get the next contact
		dContact = get_next_contact(dCampaign['_id'])

		# If there's none, pause the campaign and move on to the next one
		if not dContact:
			campaign.pause(dCampaign['_id'])
			break

		#  If the alias is missing, set it to the name
		if 'alias' not in dContact or not dContact['alias']:
			dContact['alias'] = dContact['name']

		# Generate the translation table
		dTpl = {
			r'{_id}': dContact['campaign_contact_id'],
			r'{name}': dContact['name'],
			r'{alias}': dContact['alias'],
			r'{company}': dContact['company'],
			r'{email_address}': dContact['email_address']
		}

		print('=' * 40)

		# Generate the subject using the contacts details
		sSubject = strtr(dCampaign['subject'], dTpl)
		print('Subject: %s' % sSubject)

		# Generate the email using the contact details
		sContent = strtr(dCampaign['content'], dTpl)
		print('Content: %s' % sContent)
