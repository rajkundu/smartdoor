import os
from twilio.rest import Client
from flask import Flask, request
import config
import subprocess
import json
from pathlib import Path
SCRIPT_PARENT_DIR = Path(__file__).parent.absolute()
HANDLER_DATA_JSON = SCRIPT_PARENT_DIR / "handler_data.json"

client = Client(config.ACCOUNT_SID, config.AUTH_TOKEN)

app = Flask(__name__)

@app.route("/", methods=['POST'])
def handler():
    """Handle conversation webhook triggers"""
    print(request.values)
    
    author = request.values.get("Author", None)
    body = request.values.get("Body", None)
    sid = request.values.get("ConversationSid", None)
    conversation = client.conversations.conversations(sid).fetch()

    # Read in user JSON

    if(conversation.unique_name == config.AUTH_CONVERSATION_NAME):
        print("This was sent in the auth group chat")
    elif(len(conversation.participants.list()) == 1):
        print(author)
        pass

    return str()

if __name__ == "__main__":
    # Start vortex
    vortex_process = subprocess.Popen(["vortex", "-s", config.WEBHOOK_URL.split("://")[1], "--host", "127.0.0.1", "--port", str(config.WEBHOOK_PORT), "--provider", "http"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    vortex_process.stdin.write(str(str(config.VORTEX_PIN) + "\n").encode())
    vortex_process.stdin.close()
    
    print("====================")
    print(f"url: {config.WEBHOOK_URL}")
    print(f"port: {config.WEBHOOK_PORT}")
    print("====================")

    app.run(port=config.WEBHOOK_PORT, debug=False)
