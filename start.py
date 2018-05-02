import random
import DBConnect
import ListObj

from flask import Flask, request
from pymessenger.bot import Bot

import model_service

app = Flask(__name__)

ACCESS_TOKEN = 'EAAa1SOnFK8cBAKrh5Sv0ZADKdyWdsMdbtcLIjZBt2esiB66LnkALGpXPSAXZBWB79GuEPXXZCFkE4hlQPqFb67zqCqcS6opBElXNRxH8wuLPDD5JN45YadcKkk7UDndVSsCNtCTZA7ZBqzxBfHRxqvd1AmEdm6OTGhuVHdP4GwdjjgO3FuUO7Q'
VERIFY_TOKEN = 'test_token'

HIKING = ["https://www.banfftours.com/wp-content/uploads/2017/01/Hiking-Lake-Louise-1.jpg",
          "https://res.cloudinary.com/simpleview/image/upload/c_fill,f_auto,h_536,q_65,w_768/v1/clients/norway/hovdenhikingnorway_f5c75ba6-7f5c-43d5-919d-51452136b030.jpg",
          "https://www.kamloopshikingclub.net/wp-content/uploads/2014/09/hikers-silhouette.jpg"]

SAFARI = ["https://www.zicasso.com/sites/default/files/styles/original_scaled_down/public/headerimages/tour/African-Safari-Lion-LT-Header.jpg",
          "https://tcc.com.ua/storage/gallery/images/hotels/05c/05c5c45c8fd2b3cd3b24dea913499f28.jpg",
          "https://d1ljaggyrdca1l.cloudfront.net/wp-content/uploads/2017/04/Giraffe-on-a-walking-safari-in-Etosha-Namibia-1600x900.jpg"]
 
DOG = ["https://amp.businessinsider.com/images/528127d66bb3f7c12136f884-750-562.jpg",
       "https://www.europetnet.com/images/dogbreeds/255.jpg",
       "https://www.billingsk9coaching.com/wp-content/uploads/2018/02/group1.png"]
 
FOOD = ["https://www.rd.com/wp-content/uploads/2017/10/12_Citrus_Healthy-Holiday-Food-Gifts-Instead-of-Fruit-Cake_524210419-ch_ch.jpg",
        "https://www.boxpark.co.uk/assets/Uploads/_resampled/FillWyIxOTIwIiwiMTA4MCJd/Bao-Bao-Holder3.jpg",
        "https://pantograph0.goldbely.com/cfill-h630-w1200/uploads/merchant/main_image/559/hancock-gourmet-lobster-co.c62365d58493722415029905459b0cc6.jpg"]

EXCEPTION_TEXT = "Sorry! I don't have any suggestions :( Please tell me any other interest of yours.\nDo you want more suggestions?"
KEYWORD_RECEIVED_TEXT = "That’s great! What place do you live in?"
GREETINGS = "Please share with me some interests or send me some photos of your interests."
GREETINGS2_TEXT = "Welcome to Groupbot I can help you easily find groups for you based on your interests."


bot = Bot(ACCESS_TOKEN)

user_ids = {}

recognizer = model_service.instance


def send_groups_message(recipient_id, keyword, group_urls):
    images = HIKING
 
    if keyword.lower() == "hiking":
        images = HIKING
    elif keyword.lower() == "food":
        images = FOOD
    elif keyword.lower() == "dog":
        images = DOG
    elif keyword.lower() == "safari":
        images = SAFARI
 
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
        "title": "Check it out!",
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
                    send_message(recipient_id, GREETINGS)
                elif message.get('message'):
                    recipient_id = message['sender']['id']
                    if recipient_id in user_ids:
                        if user_ids[recipient_id].once:
                            user_ids[recipient_id].once = False
                            bot.send_raw(greet_btn(recipient_id, "Do you want more suggestions?"))
                            return "Message Processed"
                        if user_ids[recipient_id].interest is None:
                            if message.get('message').get('attachments'):
                                message = message.get('message')
                                image_url = message.get('attachments')[0].get('payload').get('url')
                                keyword = recognizer.recognize(image_url)
                                print(keyword)
                                if keyword is None:
                                    bot.send_raw(greet_btn(recipient_id, EXCEPTION_TEXT))
                                    return "Message Processed"
                                else:
                                    user_ids[recipient_id].interest = keyword.strip()
                                    send_message(recipient_id, KEYWORD_RECEIVED_TEXT)
                            else:
                                user_ids[recipient_id].interest = message['message'].get('text')
                                send_message(recipient_id, KEYWORD_RECEIVED_TEXT)
                        else:
                            user_ids[recipient_id].location = message['message'].get('text')
                            response_sent_text = DBConnect.getURL(user_ids[recipient_id].location, user_ids[recipient_id].interest)
                            if len(response_sent_text) == 0:
                                bot.send_raw(greet_btn(recipient_id, EXCEPTION_TEXT))
                                return "Message Processed"
                            else:
                                str = send_groups_message(recipient_id, user_ids[recipient_id].interest, response_sent_text)
                                print(str)
                                bot.send_raw(str)
                                user_ids[recipient_id].interest =None
                                user_ids[recipient_id].location = None
                                user_ids[recipient_id].once = True
                    else:
                        bot.send_raw(greet_btn(recipient_id, GREETINGS2_TEXT))
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

if __name__ == '__main__':
    app.run()

