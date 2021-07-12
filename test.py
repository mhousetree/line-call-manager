from flask import Flask, request, abort
import os
import r

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import datetime

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GROUP_ID = os.environ["GROUP_ID"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def main():
    conn = r.connect()
    date_next_call = conn.get('reserved_date')
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    text = '現在の時刻は' + dt_now.strftime('%Y年%m月%d日 %H:%M') + 'です。\n次回の通話は' +  date_next_call + 'までに行われます。'
    pushText = TextSendMessage(text)
    line_bot_api.push_message(GROUP_ID, messages=pushText)

if __name__ == "__main__":
    main()