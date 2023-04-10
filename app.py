from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    FollowEvent
)
import os, traceback

import twder, database
from text_messages import *

app = Flask(__name__)

# Retrieve API tokens

# 1. If deployed on Heroku cloud: get keys from environment variables
channel_access_token = os.environ.get('CHANNEL_ACCESS_TOKEN')
channel_secret = os.environ.get('CHANNEL_SECRET')

# 2. If tested on Local Machine: get keys from the file
if channel_access_token is None or channel_secret is None:
    keys = open("keys.txt", "r")
    channel_access_token =  keys.readline().strip()
    channel_secret = keys.readline().strip()
    keys.close()

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

currency_alias = [('美金','美元', '美', 'USD', 'US'), ('港幣', '港', 'HKD', 'HK'), ('英鎊', '英', 'GBP'),
         ('澳幣', '澳州',  'AUD'), ('加拿大幣', '加拿大','CAD'), ('新加坡幣', '新加坡', 'SGD'), 
         ('瑞士法郎', '瑞士', 'CHF'), ('日圓', '日幣', '日本', 'JPY'), 
         ('南非幣', 'ZAR'), ('瑞典幣', 'SEK'), ('紐元', 'NZD'), 
         ('泰幣', 'THB'), ('菲國比索', 'PHP'), ('印尼幣', 'IDR'), ('歐元', 'EUR'), 
         ('韓元', 'KRW'), ('越南盾', 'VND'), ('馬來幣', 'MYR'), ('人民幣', 'CNY')]
currency_dict = dict(zip(twder.currencies(), currency_alias))

# https://cd92-27-33-126-123.ngrok-free.app

@app.route("/", methods=['GET'])
def home():
    return f"""<p>This is the Webhook URL of CurrencyReminder LINE Bot to process events sent by LINE users!<p/>"""
    

@app.route("/callback", methods=['POST'])
def callback():
    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(body)
    

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    # add new user to the database
    profile = line_bot_api.get_profile(event.source.user_id)
    success = database.add_user(profile)

    if not success:
        print(f"app: handle_follow: failed to add user with id '{profile.user_id}' to the database")
    else:
        line_bot_api.reply_message(event.reply_token,
            [welcome_message, HELP_MESSEGE, list_all_currencies])



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text.strip()
    user_id = event.source.user_id

    print(f"\n\nRECEIVED MESSAGE: {message}\n\n")
    for code, alias in currency_dict.items():
        if message.upper() in alias:
            content = ""
            try:
                content = currency_rate_report(code)   
                line_bot_api.reply_message(event.reply_token,
                    TextSendMessage(
                        text=content
                    )
                )
            except ValueError:
                line_bot_api.reply_message(event.reply_token,
                        TextSendMessage(text="很抱歉，目前查無此匯率"))
                
    try:
        ### Add userId to json file
        if message.lower() == "help":
            line_bot_api.reply_message(
                event.reply_token,
                HELP_MESSEGE)

        elif message.lower() == "all":

            line_bot_api.reply_message(
                event.reply_token,
                list_all_currencies())
        
        elif message.lower() == "role":
            role = database.get_role(user_id)
            if role is not None:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"Your role is \"{role}\"")
                )

            else:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"No role found")
                )

        else:
            line_bot_api.reply_message(event.reply_token,
                [INVALID_MESSEGE, HELP_MESSEGE])

    except Exception as e:
        line_bot_api.reply_message(event.reply_token, 
           "很抱歉，程式運行時發生錯誤，因此無法正常運作！")
        
        traceback.print_exception()


if __name__ == "__main__":
    # On MacOS, you have to choose port other than default 5000
    # port = int(os.environ.get("PORT", 5002))
    # app.run(port=port)
    pass