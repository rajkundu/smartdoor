import os
from twilio.rest import Client
from config import ACCOUNT_SID, AUTH_TOKEN, AUTH_CONVERSATION_NAME, AUTH_CONVERSATION_PARTICIPANTS, TWILIO_PHONE_NO, TWILIO_PHONE_NAME

# This script deletes *** ALL *** Twilio conversations under your account.
# It is only meant for testing and is NOT RECOMMENDED FOR USE.

client = Client(ACCOUNT_SID, AUTH_TOKEN)

print("Are you sure that you want to delete ALL conversations? (Y/N) >> ", end="")
answer = input().lower()
if(answer == "y" or answer == "yes"):
    print("Deleting...")
    conversation_list = client.conversations.conversations.list()
    for c in conversation_list:
        c.delete()
    print("Done")
else:
    print("Canceled operation")