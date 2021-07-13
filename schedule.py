from d import get_str_dt
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import datetime
import locale

import d
import r

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GROUP_ID = os.environ["GROUP_ID"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def main():
    conn = r.connect()
    date_next_call = conn.get('reserved_date')
    dt_next_call = datetime.strptime('%Y年%m月%d日(%a) %H:%M')

    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )

    if dt_now + datetime.timedelta(minutes=15) > dt_next_call:
        text = date_next_call + "から通話予定です！"
        pushText = TextSendMessage(text)
        line_bot_api.push_message(GROUP_ID, pushText)
    else:    
        text = '現在の時刻は' + dt_now.strftime('%Y年%m月%d日(%a) %H:%M') + 'です。\n次回の通話は' +  date_next_call + 'に行われます。'
        pushText = TextSendMessage(text)
        line_bot_api.push_message(GROUP_ID, messages=pushText)

if __name__ == "__main__":
    main()