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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pprint import pformat
from random import uniform
import smtplib
from time import sleep

# Pip imports
import arrow

# Record imports
from records.contact import campaign, campaign_contact, contact, sender

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
		dContact = contact.Contact.get(dCampaignContact['_contact'], raw = True)

		# If they don't exist, remove them and start again
		if not dContact:
			campaign_contact.CampaignContact.remove(dCampaignContact['_id'])
			continue

		# If the contact is unsubscribed, remove them and start again
		if dContact['unsubscribed']:
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

	# Get the domain for tracking / unsubscribing
	sTrackRoot = 'https://%s/' % \
		config.track.domain('track.contact.local')
	sUnsubscribeRoot = 'https://%s/' % \
		config.unsubscribe.domain('unsubscribe.contact.local')

	# Loop forever
	while True:

		# Fetch any campaigns that are at or past their trigger
		lCampaigns = campaign.Campaign.filter(
			{ 'next_trigger': { 'lte': int(arrow.get().timestamp()) } },
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
				r'{email_address}': dContact['email_address'],
				r'{unsubscribe_url}': '%s%s' % (
					sUnsubscribeRoot, dContact['campaign_contact_id']
				)
			}

			# Generate the subject using the contacts details
			sSubject = strtr(dCampaign['subject'], dTpl)

			# Generate the email using the contact details
			sContent = strtr(dCampaign['content'], dTpl)

			# Add the tracking pixel to the start of the content
			sContent = '<img src="%s%s" />' % (
				sTrackRoot, dContact['campaign_contact_id']
			) + sContent

			# Generate the email
			message = MIMEMultipart()
			message['From'] = dSender['email_address']
			message['To'] = dContact['email_address']
			message['Subject'] = sSubject
			message['List-Unsubscribe'] = '<%soneclick/%s>' % (
				sUnsubscribeRoot, dContact['campaign_contact_id']
			)
			message.attach(MIMEText(sContent, 'html'))

			# Connect to the SMTP server
			with smtplib.SMTP(dSender['host'], dSender['port']) as mail:

				# If we need tls
				if dSender['tls']:
					mail.starttls()

				# Login
				mail.login(dSender['email_address'], dSender['password'])

				# Send the email
				try:
					mail.send_message(message)

					# Mark the message as sent and delivered
					campaign_contact.sent_and_delivered(
						dContact['campaign_contact_id']
					)

				except Exception as e:
					print(e)

					# Mark the message as sent
					campaign_contact.sent(
						dContact['campaign_contact_id']
					)

			# Set the next trigger for the campaign
			campaign.set_next(
				dCampaign['_id'],
				[ dCampaign['min_interval'], dCampaign['max_interval'] ]
			)