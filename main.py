import time

from handlers import send_message, get_updates, next_step
from commands.lowprice import low_price
from user import User, users_dict, users_action_dict


def check_button(chat_id, message_id, data):
    if users_action_dict[chat_id][0] == '/lowprice':
        low_price(chat_id, message_id, data, step=users_action_dict[chat_id][1])


def check_message(chat_id, message_id, messages):
    for message in messages.lower().split(','):
        if chat_id not in users_action_dict.keys():
            users_dict[chat_id] = User()

            if message == '/help':
                send_message(chat_id, 'Напиши /lowprice')
            elif message == '/lowprice':
                next_step(command=message, chat_id=chat_id, step=0)
                low_price(chat_id, message_id, message, step=users_action_dict[chat_id][1])
            else:
                send_message(chat_id, 'Я тебя не понимаю, напиши /help')
        else:
            if message == '/help':
                send_message(chat_id, 'Напиши /lowprice')
                users_action_dict.pop(chat_id)

            if users_action_dict[chat_id][0] == '/lowprice':
                low_price(chat_id, message_id, message, step=users_action_dict[chat_id][1])


def main():
    try:
        update_id = get_updates()[-1]['update_id']
        while True:
            messages = get_updates(update_id)

            for message in messages:
                if update_id < message['update_id']:
                    update_id = message['update_id']

                    if 'callback_query' in message.keys():
                        data = message['callback_query']['data']
                        text_button = ''

                        for button in message['callback_query']['message']['reply_markup']['inline_keyboard']:
                            if button[0]['callback_data'] == data:
                                text_button = button[0]['text']

                        with open(f"logs\\{message['callback_query']['from']['id']}.txt", 'a', encoding='utf-8') as file:
                            file.write(f"callback: ({text_button, data})\n")

                        check_button(message['callback_query']['from']['id'],
                                     message['callback_query']['message']['message_id'],
                                     (data, text_button))
                    else:
                        with open(f"logs\\{message['message']['chat']['id']}.txt", 'a', encoding='utf-8') as file:
                            file.write(f"message: {message['message']['text']}\n")

                        check_message(message['message']['chat']['id'],
                                      message['message']['message_id'],
                                      message['message']['text'])
    except IndexError:
        main()
    except ConnectionError:
        time.sleep(1)
        main()
    except Exception as error:
        print(f'{type(error).__name__}: {error}')
        main()


if __name__ == '__main__':
    main()
