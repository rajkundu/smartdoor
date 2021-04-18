import os
from twilio.rest import Client
from flask import Flask, request
from config import ACCOUNT_SID, AUTH_TOKEN, TWILIO_PHONE_NO, AUTH_CONVERSATION_NAME, TWILIO_PHONE_NAME, AUTH_CONVERSATION_PARTICIPANTS

client = Client(ACCOUNT_SID, AUTH_TOKEN)

app = Flask(__name__)

@app.route("/", methods=['POST'])
def sms_reply():
    """Send a dynamic reply to an incoming text message"""
    print(request.values)
    body = request.values.get("Body", None)
    conversation = client.conversations.conversations(request.values.get("ConversationSID", None))

    if(conversation.unique_name == AUTH_CONVERSATION_NAME):
        print("This was sent in the auth group chat")
    elif(len(conversation.participants.list()) == 1):
        pass

    return str()

if __name__ == "__main__":
    app.run(debug=True)
