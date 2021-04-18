import os
from twilio.rest import Client
from api_access import ACCOUNT_SID, AUTH_TOKEN
from config import AUTH_CONVERSATION_NAME, AUTH_CONVERSATION_PARTICIPANTS, TWILIO_PHONE_NO, TWILIO_PHONE_NAME

# This script deletes *** ALL *** Twilio conversations under your account.
# It is only meant for testing and is NOT RECOMMENDED FOR USE.

client = Client(ACCOUNT_SID, AUTH_TOKEN)

conversation_list = client.conversations.conversations.list()
for c in conversation_list:
    c.delete()
