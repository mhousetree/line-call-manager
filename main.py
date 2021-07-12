from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot import exceptions
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os
import datetime

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def get_day_of_week_jp(dt):
    w_list = ['月', '火', '水', '木', '金', '土', '日']
    return w_list[dt.weekday()]

def get_day_of_next_call(dt):
    next_weekday = 6 if dt.weekday() < 3 else 8
    days_delta = next_weekday - dt.weekday()
    return dt + datetime.timedelta(days=days_delta)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '通話完了':
        dt_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )
        finished_time = dt_now.strftime('%Y年%m月%d日 %H:%M')
        date_next_call = get_day_of_next_call(dt_now)
        text = finished_time + 'に通話が完了しました。\n次回の通話は' + date_next_call.strftime('%Y年%m月%d日') + '([])'.format(get_day_of_week_jp(date_next_call)) + 'までに行います。'
    else:
        text = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text))


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)