# coding=utf8
""" Error Codes

Project error codes
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2024-01-11"

EMAIL_UNSUBSCRIBED = 2000
"""Email Unsubscribed

Error in case someone tries to add a contact that's already been unsubscribed
"""

CONTACT_UNSUBSCRIBED = 2001
"""Contact Unsubscribed

Error in case someone tries to update a contact that's already been unsubscribed
"""

SENDER_BEING_USED = 2002
"""Sender being used

Error in case someone tries to delete a sender record that is still associated
with unfinished campaigns
"""