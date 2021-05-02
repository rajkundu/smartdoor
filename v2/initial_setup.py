import os
from twilio.rest import Client
import config
import subprocess

client = Client(config.ACCOUNT_SID, config.AUTH_TOKEN)

conversation_list = client.conversations.conversations.list()
OUTPUT_DIV = "=" * 40

# Set Twilio webhook URL
webhook = client.conversations.configuration.webhooks().update(pre_webhook_url="", post_webhook_url=(config.WEBHOOK_URL + config.WEBHOOK_DIR), method='POST', filters=['onMessageAdded'])

# Delete conversation if it already exists (e.g. if it was created by users, it must be recreated by Twilio/this script to be used properly)
for c in client.conversations.conversations.list():
    participant_numbers = set()
    for p in c.participants.list():
        address_key = None
        for key in p.messaging_binding.keys():
            if "address" in key:
                address_key = key
        participant_numbers.add(p.messaging_binding[address_key])
    if(c.unique_name == config.AUTH_CONVERSATION_NAME or participant_numbers == set(list(config.AUTH_CONVERSATION_PARTICIPANTS.keys()) + [config.TWILIO_PHONE_NO])):
        print(OUTPUT_DIV)
        print()
        print(f"Found existing conversation:\nSID: '{c.sid}'\nUnique name: '{c.unique_name}'\nFriendly name: '{c.friendly_name}'")
        print()
        c.delete()

# Create conversation
conversation = client.conversations.conversations.create(friendly_name=config.AUTH_CONVERSATION_NAME, unique_name=config.AUTH_CONVERSATION_NAME)
print(OUTPUT_DIV)
print()
print(f"Created new conversation:\nSID: '{conversation.sid}'\nUnique name: '{conversation.unique_name}'\nFriendly name: '{conversation.friendly_name}'")
print()

# Add participants - first Twilio user, then regular SMS users
conversation.participants.create(identity=config.TWILIO_PHONE_NAME, messaging_binding_projected_address=config.TWILIO_PHONE_NO)
print(f"Added {config.TWILIO_PHONE_NAME} ({config.TWILIO_PHONE_NO}) to conversation.")
print()
for number in config.AUTH_CONVERSATION_PARTICIPANTS.keys():
    conversation.participants.create(messaging_binding_address=number)
    print(f"Added {config.AUTH_CONVERSATION_PARTICIPANTS[number]} ({number}) to conversation.")
print()

# Send test message
conversation.messages.create(author=config.TWILIO_PHONE_NAME, body=f"The authentication conversation '{config.AUTH_CONVERSATION_NAME}' has been set up successfully.")
print(OUTPUT_DIV)
print()
print("Sucessfully set up authentication conversation.")
print()
print(OUTPUT_DIV)
