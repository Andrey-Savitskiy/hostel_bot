#!/usr/bin/env python3
#
# A library that allows to create an inline calendar keyboard.
# grcanosa https://github.com/grcanosa
#
"""
Base methods for calendar keyboard creation and processing.
"""

import datetime
import calendar
import json
import requests
from handlers import delete_error_messages, edit_message_button, send_message, URL, TOKEN
from user import users_dict


def create_inline_calendar(chat_id, text):
    data = {'chat_id': chat_id, 'text': text,
            'reply_markup': create_calendar()}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def inline_handler_calendar(chat_id, message_id, message, step=False):
    text_date_in = 'Выберите дату заезда:'
    text_date_out = 'Выберите дату выезда:'

    if step:
        text_date = text_date_out
    else:
        text_date = text_date_in

    selected, date = process_calendar_selection(chat_id, message_id, message, text_date)

    if selected:
        text = date.strftime('%d.%m.%Y')

        if not step:
            if is_date_correct(date, step):
                users_dict[chat_id].date_in = date
                edit_message_button(chat_id, message_id, f'Дата заезда: {text}')
                create_inline_calendar(chat_id, text_date_out)
                return True
        else:
            if is_date_correct(date, step, date_in=users_dict[chat_id].date_in):
                users_dict[chat_id].date_out = date
                edit_message_button(chat_id, message_id, f'Дата выезда: {text}')
                return True

        response = send_message(chat_id, 'Введена некорректная дата, попробуйте еще раз.').json()
        users_dict[chat_id].errors.append(response['result']['message_id'])

        if len(users_dict[chat_id].errors) > 1:
            delete_error_messages(chat_id, not_last=True)

    return False


def is_date_correct(date: datetime, step, date_in: datetime=None):
    now = datetime.datetime.date(datetime.datetime.now())
    date = datetime.datetime.date(date)

    if not step:
        if date < now:
            return False
        else:
            return True
    else:
        date_in = datetime.datetime.date(date_in)
        if date <= date_in:
            return False
        else:
            return True


def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])


def create_calendar(year=None, month=None):
    """
    Create an inline markup with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    """
    now = datetime.datetime.now()
    year = now.year if year is None else year
    month = now.month if month is None else month
    data_ignore = create_callback_data("IGNORE", year, month, 1)
    markup = {"inline_keyboard": []}
    # First row - Month and Year
    row = [{"text": calendar.month_name[month] + " " + str(year), "callback_data": data_ignore}]
    markup["inline_keyboard"].append(row)
    # Second row - Week Days
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append({"text": day, "callback_data": data_ignore})
    markup["inline_keyboard"].append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append({"text": " ", "callback_data": data_ignore})
            else:
                row.append({"text": "{}".format(day), "callback_data": create_callback_data("DAY", year, month, day)})
        markup["inline_keyboard"].append(row)
    # Last row - Buttons
    row = [{"text": "<", "callback_data": create_callback_data("PREV-MONTH", year, month, day)},
           {"text": " ", "callback_data": data_ignore},
           {"text": ">", "callback_data": create_callback_data("NEXT-MONTH", year, month, day)}]
    markup["inline_keyboard"].append(row)

    return json.dumps(markup)


def process_calendar_selection(chat_id, message_id, message, button_text):
    """
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    """
    ret_data = (False, None)

    try:
        (action, year, month, day) = message.split(";")
    except ValueError:
        return ret_data

    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        ret_data = False, datetime.datetime(int(year), int(month), int(day))
    elif action == "DAY":
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        edit_message_button(chat_id, message_id, button_text,
                            reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        edit_message_button(chat_id, message_id, button_text,
                            reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        pass
        # UNKNOWN
    return ret_data
