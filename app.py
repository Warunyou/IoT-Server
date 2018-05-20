from flask import Flask, request, abort, make_response
from flask_httpauth import HTTPBasicAuth
import os

import requests, json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)


CHANNEL_SECRET = os.environ.get('provider_channel_secret')
CHANNEL_ACCESS_TOKEN = os.environ.get('provider_channel_access_token')

USER_RAM_TOKEN = os.environ.get('user_ram_id')
USER_TOP_TOKEN = os.environ.get('user_top_id')



line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

db =''

#---------------------------------------------------------------------------------------
# Web Hook For LINE
#---------------------------------------------------------------------------------------
@app.route('/line_callback', methods=['POST'])
def line_callback():

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return request.data




@app.route('/')
def index():
	return CHANNEL_SECRET

@app.route('/hello', methods=['GET'])
def hello():
	username = request.args.get('name')
	return 'hello ' + username

@app.route('/callback', methods=['POST'])
def callback():
	payload = request.get_json()
	json_string = json.dumps(payload)
	data_dict = json.loads(json_string)

	user_name = data_dict['name']
	user_id = data_dict['id']
	user_message = data_dict['message']

	result = 'JSON String: '+ json_string + '\n'
	result = result + 'user_id: ' + user_id + '\n'
	result = result + 'user_name: ' + user_name + '\n'
	result = result + 'user_message: ' + user_message + '\n'

	return result

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	global db
	text = event.message.text #message from user
	db = text

@app.route('/push_to_line', methods=['POST'])
def push_to_line():
	payload = request.get_json()
	json_string = json.dumps(payload)
	data_dict = json.loads(json_string)

	user_name = data_dict['name']
	user_id = data_dict['id']
	user_message = data_dict['message']

	line_bot_api.push_message(USER_RAM_TOKEN, TextSendMessage(text=user_message))

	result = {'status':'success'}
	return json.dumps(result)

@app.route('/message_checker',methods=['POST'])
def message_checker():
	global db
	if db !='':
		temp = db
		db = ''
		return temp
	else:
		return 'None'

if __name__ == "__main__":
    app.run()