import os
from twilio.rest import Client
from flask import Flask, request
import config
import subprocess
from pathlib import Path
SCRIPT_PARENT_DIR = Path(__file__).parent.absolute()

client = Client(config.ACCOUNT_SID, config.AUTH_TOKEN)

app = Flask(__name__)

@app.route(config.WEBHOOK_DIR, methods=['POST'])
def sms_reply():
    """Send a dynamic reply to an incoming text message"""
    print(request.values)
    
    body = request.values.get("Body", None)
    sid = request.values.get("ConversationSid", None)
    conversation = client.conversations.conversations(sid).fetch()

    if(conversation.unique_name == config.AUTH_CONVERSATION_NAME):
        print("This was sent in the auth group chat")
    elif(len(conversation.participants.list()) == 1):
        pass

    return str()

if __name__ == "__main__":
    # Connect to ngrok
    result = subprocess.run(["bash", str(SCRIPT_PARENT_DIR / "ngrok_start.sh")], stdout=subprocess.PIPE)
    if(result.returncode != 0):
        print(f"Return code: {result.returncode}")
        try:
            stderr = result.stderr.decode('utf-8')
            print("STDERR:")
            print(stderr)
        except:
            pass
        try:
            stdout = result.stdout.decode('utf-8')
            print("STDOUT:")
            print(stdout)
        except:
            pass
    # Parse output data of shell script into dictionary
    output_data = dict()
    outputlines = result.stdout.decode('utf-8').rstrip().split("\n")
    for line in outputlines:
        line_data = line.split("=")
        output_data[line_data[0]] = line_data[1]
    
    # Get ngrok url
    ngrok_url = "https://" + output_data["NGROK_URL"]
    handler_port = output_data["HANDLER_PORT"]
    print()
    print(f"ngrok url: {ngrok_url}")
    print(f"port: {handler_port}")
    print()
    webhook = client.conversations.configuration.webhooks().update(pre_webhook_url="", post_webhook_url=ngrok_url, method='POST', filters=['onMessageAdded'])
    app.run(port=handler_port, debug=False)
