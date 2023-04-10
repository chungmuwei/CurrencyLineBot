from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton, MessageAction,
)
import rate, twder

def welcome_message(name):
    return TextSendMessage(text=f"""{name}您好：歡迎您使用Currency Reminder。請閱讀以下訊息來了解目前支援的功能以及使用方式，""")

HELP_MESSEGE = TextSendMessage(text=f"""目前支援的指令如下：
1. \"help"：查看使用方式
2. \"all\"：查看支援的貨幣種類及其貨幣代碼
3. \"<貨幣代碼>或<中文名稱>\"：查看該貨幣兌台幣即時匯率。例如：輸入「AUD」或「澳幣」查詢澳幣目前匯率""",
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