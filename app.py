import random
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)

ACCESS_TOKEN = 'EAACrVDMImJYBAKBMsbOZBzZAuef9ormXEveFVVwnWAIbdQlFbFqhqF0noHaoxJaGmPKb67Tv2uHGz8MaUOyOHVPCXV9TM5IX25YZCFtBCvsykfSBpW7ia4Wg5knhTw9oMmTN6UHsdTjkyLjeHd5XSnOvclTXn0NkEmGsPZBoQkp103NImt1F'
VERIFY_TOKEN = 'test_token'

bot = Bot(ACCESS_TOKEN)


@app.route('/webhook', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args['hub.verify_token']
        return verify_fb_token(token_sent)
    else:
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_group_message(recipient_id, "https://www.facebook.com/groups/hikeitbabydartmouth")
                    # send_message(recipient_id, response_sent_text)
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
        return "Message Processed"


def send_group_message(self, recipient_id, group_url):
    payload = {
        "recipient": {
            "id": recipient_id
        },
        "messaging_type": "response",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "This is a button template with a few different buttons.",
                    "buttons": [
                        {
                            "type": "web_url",
                            "title": "Preview Button",
                            "url": group_url,
                            "webview_height_ratio": "compact"
                        },
                        {
                            "type": "web_url",
                            "title": "URL Button",
                            "url": group_url
                        }
                    ]
                }
            }
        }
    }
    return self.send_raw(payload)


def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return 'Invalid verification token'


def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return 'Success'


def get_message():
    sample_responses = ["Awesone!", "Cool!", "Go Ahead!"]
    return random.choice(sample_responses)


if __name__ == '__main__':
    app.run()
