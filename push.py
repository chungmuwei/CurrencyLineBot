from flask import Flask, request, abort
from linebot import (
    LineBotApi
)
from linebot.models import (
    TextSendMessage
)

import schedule, time

from app import line_bot_api


def load_subscribers():
    f = open("data/userId.txt", "r")
    return f.readlines()

subscribers = load_subscribers()
    

def push_daily_report():
    # Send push messages to all users which added the bot as a friend
    line_bot_api.broadcast(messages=TextSendMessage(text="Daily broadcast!"))



if __name__ == "__main__":
    push_daily_report()
    # schedule.every().day.at("09:00").do(push_daily_report)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)