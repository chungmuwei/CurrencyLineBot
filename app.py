from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)

import os, rate, twder

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

# https://cd92-27-33-126-123.ngrok-free.app

# def load_subscribers():
#     f = open("data/userId.txt", "r")
#     return set(f.readlines())

# subscribers = load_subscribers()

INFO_MESSEGE = TextSendMessage(text=f"""目前支援的指令如下：
1. \"info"：查看使用方式
2. \"all\"：查看支援的貨幣種類及其貨幣代碼
3. \"<貨幣代碼>\"：查看該貨幣兌台幣即時匯率""",
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="all", text="all")),
                QuickReplyButton(action=MessageAction(label="AUD", text="AUD")),
                QuickReplyButton(action=MessageAction(label="USD", text="USD")),
                QuickReplyButton(action=MessageAction(label="JPY", text="JPY"))
            ]))

INVALID_MESSEGE = TextSendMessage(text="很抱歉，我無法辨識您的指令！")

def list_all_currencies():
    content = "目前支援的貨幣如下：\n"
    content += "\n".join(twder.currency_name_dict().values())
    return TextSendMessage(text=content, quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="AUD", text="AUD")),
                QuickReplyButton(action=MessageAction(label="USD", text="USD")),
                QuickReplyButton(action=MessageAction(label="JPY", text="JPY"))
            ]))


def currency_rate_report(currency):
    now_rate = rate.get_now_rate(currency)
    yesterday_rate = rate.get_yesterday_rate(currency)
    diff = now_rate - yesterday_rate
    diff_percentage = diff / now_rate * 100
    ret_str = ""
    
    ret_str += f"{currency}/TWD={now_rate}\n"

    if diff > 0:
        ret_str += "相較昨日 +{:.4f}(🔺{:.4f}%)".format(diff, diff_percentage)
    elif diff < 0:
        ret_str += "相較昨日 {:.4f}(🔻{:.4f}%)".format(diff, diff_percentage)
    else:
        ret_str += "與昨日相同"
    
    return ret_str

@app.route("/", methods=['GET'])
def home():
    return "This is the Webhook URL of my CurrencyReminder LINE Bot to process events sent by LINE platform!"
    

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ### Add userId to json file
    message = event.message.text.strip()

    if message.lower() == "info":
        line_bot_api.reply_message(
            event.reply_token,
            INFO_MESSEGE)

    elif message.lower() == "all":

        line_bot_api.reply_message(
            event.reply_token,
            list_all_currencies())
    
    elif message.upper() in rate.list_currencies():
        content = ""
        try:
            content = currency_rate_report(message.upper())   
            line_bot_api.reply_message(event.reply_token,
                TextSendMessage(
                    text=content
                )
            )
        except ValueError:
           line_bot_api.reply_message(event.reply_token,
                TextSendMessage(
                    text="很抱歉，目前查無此匯率"
                )
            ) 

    else:
        line_bot_api.reply_message(event.reply_token,
            [INVALID_MESSEGE, INFO_MESSEGE])
            


if __name__ == "__main__":
    # On MacOS, you have to choose port other than default 5000
    port = int(os.environ.get("PORT", 5002))
    localhost = "127.0.0.1"
    app.run(port=port, debug=True)