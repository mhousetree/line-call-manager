import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

def get_dt_of_next_call(dt):
    next_weekday = 6 if dt.weekday() < 3 else 8
    days_delta = next_weekday - dt.weekday()
    return dt + datetime.timedelta(days=days_delta)

def get_str_dt(dt):
    return dt.strftime('%Y/%m/%d(%a) %H:%M')
