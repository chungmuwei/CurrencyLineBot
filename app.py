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

# '0FmaYmoBD+O1kPOtna88s5uehDgVbGBNQaoFHA6L1nBOsunQMYg5vVjPltt57j+/uH305Uys6wcmXTxjAb2QBDQwF0/68WSwIWmUl9TfIT4jKIx+3LIIdn6TbBKAbMoaAlt2OkUkWjG2QuNDQuCBLQdB04t89/1O/w1cDnyilFU='
# 'ce8c604a308615d0f101c2bbbbab1e5f'
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

# https://a0bf-27-33-126-123.ngrok.io/callback

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



@app.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return "Hello Heroku"
    
    if request.method == 'POST':
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)