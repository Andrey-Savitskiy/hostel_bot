from handlers import *
from user import users_action_dict
from inline_calendar import create_inline_calendar, inline_handler_calendar


def low_price(chat_id, message_id, message, step):
    command = '/lowprice'
    try:
        if step == 0:
            create_inline_calendar(chat_id, 'Выберите дату заезда:')
            next_step(command=command, chat_id=chat_id, step=step + 1)
        elif step == 1:
            if inline_handler_calendar(chat_id, message_id, message[0]):
                delete_error_messages(chat_id)
                next_step(command=command, chat_id=chat_id, step=step + 1)
        elif step == 2:
            if inline_handler_calendar(chat_id, message_id, message[0], step=True):
                delete_error_messages(chat_id)
                next_step(command=command, chat_id=chat_id, step=step + 1)
                get_user_part_world(chat_id, message[0])
        elif step == 3:
            if get_user_part_world(chat_id, message[0], message_id=message_id, step=True):
                get_user_country(chat_id, message[0])
                next_step(command=command, chat_id=chat_id, step=step + 1)
            else:
                send_message(chat_id, 'Воспользуйтесь клавиатурой')
        elif step == 4:
            if get_user_country(chat_id, message[0], message_id=message_id, step=True):
                get_user_town(chat_id)
                next_step(command=command, chat_id=chat_id, step=step + 1)
            else:
                send_message(chat_id, 'Воспользуйтесь клавиатурой')
        elif step == 5:
            get_user_town(chat_id, message, step=True)
            town_search(chat_id)
            next_step(command=command, chat_id=chat_id, step=step + 1)
        elif step == 6:
            if town_search(chat_id, message=message, message_id=message_id, step=True):
                get_user_hostel_limit(chat_id, message)
                next_step(command=command, chat_id=chat_id, step=step + 1)
            else:
                send_message(chat_id, 'Воспользуйтесь клавиатурой')
        elif step == 7:
            if get_user_hostel_limit(chat_id, message, step=True):
                inline_keyboard_bool(chat_id)
                next_step(command=command, chat_id=chat_id, step=step + 1)
        elif step == 8:
            if inline_keyboard_bool(chat_id, message=message[0], message_id=message_id, step=True):
                if message[0] == 'Да':
                    get_user_photo_limit(chat_id, message)
                    next_step(command=command, chat_id=chat_id, step=step + 1)
                else:
                    hostel_search(chat_id, sort_mode='PRICE')
                    users_action_dict.pop(chat_id)
        else:
            if get_user_photo_limit(chat_id, message, step=True):
                hostel_search(chat_id, sort_mode='PRICE')
                users_action_dict.pop(chat_id)

    except SearchTownError as error:
        send_message(chat_id, error)
        get_user_town(chat_id)
    except SearchHostelError as error:
        send_message(chat_id, error)
        users_action_dict.pop(chat_id)
