HANDLER_PORT=5000
echo "HANDLER_PORT=$HANDLER_PORT"
ngrok http $HANDLER_PORT > /dev/null &
sleep 1
echo "NGROK_URL=$(curl --silent --show-error http://127.0.0.1:4040/api/tunnels | sed -nE 's/.*public_url\":\"https:..([^\"]*).*/\1/p')"
