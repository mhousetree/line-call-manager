from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot import exceptions
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, DatetimePickerTemplateAction, messages,
)
import os
import datetime
import locale

from linebot.models.actions import DatetimePickerAction
from linebot.models.events import PostbackEvent

from linebot.models.template import ButtonsTemplate

import r

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

locale.setlocale(locale.LC_TIME, 'Japanese_Japan.UTF-8')

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

def get_dt_of_next_call(dt):
    next_weekday = 6 if dt.weekday() < 3 else 8
    days_delta = next_weekday - dt.weekday()
    return dt + datetime.timedelta(days=days_delta)

def get_str_dt(dt):
    return dt.strftime('%Y/%m/%d(%a) %H:%M')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if '終了' in event.message.text:
        dt_now = datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=9))
        )
        finished_time = get_str_dt(dt_now)
        date_next_call = get_dt_of_next_call(dt_now)
        _text = finished_time + 'に通話が終了しました。\n次回の通話は' + date_next_call.strftime('%d日(%a)') + ' 22:00までに行います。'
        conn = r.connect()
        conn.set('reserved_date', date_next_call.strftime('%Y/%m/%d(%a) 22:00'))
        content = TextSendMessage(_text)
    elif '変更' in event.message.text:
        content = TemplateSendMessage(
            alt_text='日時変更',
            template=ButtonsTemplate(
                text='次の通話予定日時を変更するには\n下のボタンをタップ',
                title='日時変更',
                actions=[
                    DatetimePickerTemplateAction(
                        label='日時を選択する',
                        data='mode=datetime',
                        mode='datetime'
                    )
                ]
            )
        )
    elif '確認' in event.message.text:
        conn = r.connect()
        date_next_call = conn.get('reserved_date')
        _text = '次回の通話は' +  date_next_call + 'に行われます。'
        content = TextSendMessage(_text)
    else:
        how_to_use = [
            "{} 通話終了時 → \"終了\"".format(chr(int(0x1f4de))),
            "{} 予定日時を変更 →\"変更\"".format(chr(int(0x1f4c5))),
            "{} 予定日時を確認 →\"確認\"".format(chr(int(0x1f440))),
            "{} 使い方の確認 → \"使い方\"".format(chr(int(0x2753)))
        ]
        _text = "\n".join(how_to_use)
        content = TextSendMessage(_text)

    line_bot_api.reply_message(
        event.reply_token,
        content)

@handler.add(PostbackEvent)
def handle_postback(event):
    dt_new = datetime.datetime.strptime(event.postback.params['datetime'], '%Y-%m-%dT%H:%M')
    date_next_call = get_str_dt(dt_new)
    conn = r.connect()
    conn.set('reserved_date', date_next_call)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage("通話予定日時を " + date_next_call + " に変更しました。"))


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)