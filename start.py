import random
import DBConnect
import ListObj
import json

from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)

ACCESS_TOKEN = 'EAAa1SOnFK8cBAALWxr5s4An3GSb6KHRcd8X0vuk6rJN62gRLZB8KUu6T9pNrrzMr36MAG2x3djOVLpShYNfv4bmnuRnMYEi2fiZBUeZBQMjAvdPlolJcDJVwJ48RbH0Sux0sSAlplJZCAPWItkDxbd0i5EC6DRNtHRS3b9yjBwZDZD'
VERIFY_TOKEN = 'test_token'

HIKING = ["https://www.banfftours.com/wp-content/uploads/2017/01/Hiking-Lake-Louise-1.jpg",
          "https://res.cloudinary.com/simpleview/image/upload/c_fill,f_auto,h_536,q_65,w_768/v1/clients/norway/hovdenhikingnorway_f5c75ba6-7f5c-43d5-919d-51452136b030.jpg",
          "https://www.kamloopshikingclub.net/wp-content/uploads/2014/09/hikers-silhouette.jpg"]
 
DOG = ["https://amp.businessinsider.com/images/528127d66bb3f7c12136f884-750-562.jpg",
       "https://www.europetnet.com/images/dogbreeds/255.jpg",
       "https://www.billingsk9coaching.com/wp-content/uploads/2018/02/group1.png"]
 
FOOD = ["https://www.rd.com/wp-content/uploads/2017/10/12_Citrus_Healthy-Holiday-Food-Gifts-Instead-of-Fruit-Cake_524210419-ch_ch.jpg",
        "https://www.boxpark.co.uk/assets/Uploads/_resampled/FillWyIxOTIwIiwiMTA4MCJd/Bao-Bao-Holder3.jpg",
        "https://pantograph0.goldbely.com/cfill-h630-w1200/uploads/merchant/main_image/559/hancock-gourmet-lobster-co.c62365d58493722415029905459b0cc6.jpg"]

bot = Bot(ACCESS_TOKEN)

user_ids = {}

def send_groups_message(recipient_id, keyword, group_urls):
    images = HIKING
 
    if keyword.lower() == "hiking":
        images = HIKING
    elif keyword.lower() == "food":
        images = FOOD
    elif keyword.lower() == "dog":
        images = DOG
 
    wrapped_list = []
    for i, group_url in enumerate(group_urls):
        idx = (random.randint(0, len(images)) + i) % len(images)
        wrapped_list.append(wrap_group_message(group_url, images[idx]))
 
    payload = {
        "recipient": {
            "id": recipient_id
        },
        "messaging_type": "response",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": wrapped_list
                }
            }
        }
    }
 
    return payload
 
 
def wrap_group_message(group_url, image_url):
    msg = {
        "title": "Check it out!!",
        "image_url": image_url,
        "buttons": [
            {
                "type": "web_url",
                "title": "Preview",
                "url": group_url,
                "webview_height_ratio": "compact"
            },
            {
                "type": "web_url",
                "title": "Go to the group",
                "url": group_url
            }
        ]
    }
    return msg

def greet_btn(recipient_id, text):
    payload = {
    "recipient":{
        "id":recipient_id
    },
    "messaging_type": "response",
    "message":{
        "attachment":{
        "type":"template",
        "payload": {
        "template_type":"button",
        "text":text,
        "buttons":[
            {
            "type":"postback",
            "title":"Suggestions",
            "payload":"<POSTBACK_PAYLOAD>"
            }
        ]
        }
        }
    }
    }
    return payload


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
                print(message)
                if message.get('postback'):
                    recipient_id = message['sender']['id']
                    send_message(recipient_id, "Tell me your interest..")
                elif message.get('message'):
                    recipient_id = message['sender']['id']
                    if recipient_id in user_ids:
                        if user_ids[recipient_id].once:
                            bot.send_raw(greet_btn(recipient_id, "We can help again"))
                            return "Message Processed"
                        if user_ids[recipient_id].interest==None:
                            user_ids[recipient_id].interest = message['message'].get('text')
                            send_message(recipient_id, "Ok now tell me your location..")
                        else:
                            user_ids[recipient_id].location = message['message'].get('text')
                            response_sent_text = DBConnect.getURL(message['message'].get('text'), user_ids[recipient_id].interest)

                            if len(response_sent_text)==0:
                                send_message(recipient_id, "We currently do not have any suggestions. Please tell us any other interest of yours")
                            else:
                                str = send_groups_message(recipient_id, user_ids[recipient_id].interest, response_sent_text)
                                print(str)
                                bot.send_raw(str)
                                user_ids[recipient_id].interest=None
                                user_ids[recipient_id].location = None
                                user_ids[recipient_id].once = True
                    else:
                        bot.send_raw(greet_btn(recipient_id, "Welcome to Groupbot I can help you easily find groups for you based on your interests."))
                        user_ids[recipient_id] = ListObj.ListObj()
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

