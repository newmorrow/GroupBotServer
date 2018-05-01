import random
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)

ACCESS_TOKEN = 'EAACrVDMImJYBALgYtnfPGxxS1V8ZC4zqYIeCjfXnpLHzfXAoV3yjOydMtRvEiA9ZBZAuLFJnWLOdbqBk5ZAS5ArJJZCSzpIyNIGS1HNq4gPAf1u4IlVlzqL0O5ZBsZCaCXEda6USzaub4ZArrEud0BhDazuJP2MVA09rgZBb64zZBHns4g1cJuNrxP'
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
                    send_message(recipient_id, response_sent_text)
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
        return "Message Processed"


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
