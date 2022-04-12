from user import users_dict, users_action_dict
import requests
from loader import URL, TOKEN, LIMIT
import json
import re
from datetime import datetime
from meta_data_sort import WORLD_PART
from meta_data import DATA
from rapidapi import search_town, search_hostels, search_photo
import urllib.parse as urlcode
from Errors_class import SearchHostelError, SearchTownError


def edit_message_button(chat_id, message_id, text, reply_markup=None):
    if reply_markup is None:
        requests.get(f'{URL}{TOKEN}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={text}')
    else:
        requests.get(f'{URL}{TOKEN}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={text}'
                     f'&reply_markup={reply_markup}')


def inline_keyboard(chat_id, button_list, text):
    reply_markup = {'inline_keyboard': button_list}
    data = {'chat_id': chat_id, 'text': text,
            'reply_markup': json.dumps(reply_markup)}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def inline_keyboard_bool(chat_id, message=None, message_id=None, step=False):
    text = 'Вы хотите загрузить фото по каждому отелю?'
    data = ['Да', 'Нет']
    if not step:
        reply_markup = {'inline_keyboard': [[{'text': data[0], 'callback_data': data[0]},
                                             {'text': data[1], 'callback_data': data[1]}]]}
        data = {'chat_id': chat_id, 'text': text,
                'reply_markup': json.dumps(reply_markup)}
        requests.post(f'{URL}{TOKEN}/sendMessage', data=data)
    else:
        if message in data:
            edit_message_button(chat_id, message_id, text)
            return True
        else:
            send_message(chat_id, 'Воспользуйтесь клавиатурой')
            return False


def get_updates(offset=0):
    result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def send_message(chat_id, text, link_mode=False):
    params = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': link_mode}
    params = urlcode.urlencode(params)
    return requests.get(f'{URL}{TOKEN}/sendMessage?', params=params)


def send_photo(chat_id, photo, caption):
    params = {'chat_id': chat_id, 'photo': photo, 'caption': caption}
    params = urlcode.urlencode(params)
    return requests.get(f'{URL}{TOKEN}/sendPhoto?', params=params)


def send_media_group(chat_id, media):
    params = {'chat_id': chat_id, 'media': media}
    params = urlcode.urlencode(params)
    return requests.get(f'{URL}{TOKEN}/sendMediaGroup?', params=params)


def delete_error_messages(chat_id, not_last=False):
    if not_last:
        errors_list = users_dict[chat_id].errors[:0:-1]
    else:
        errors_list = users_dict[chat_id].errors[::-1]

    for id in errors_list:
        requests.get(f'{URL}{TOKEN}/deleteMessage?chat_id={chat_id}&message_id={id}')
        users_dict[chat_id].errors.remove(id)


def next_step(command, chat_id, step):
    users_action_dict[chat_id] = (command, step, datetime.today())


def get_user_town(chat_id, message=None, step=False) -> None:
    if not step:
        send_message(chat_id, 'Введите город:')
    else:
        users_dict[chat_id].town = message.lower()
        # print(users_dict[chat_id].town)


def get_user_hostel_limit(chat_id, message, step=False) -> bool:
    try:
        if not step:
            send_message(chat_id, 'Введите количество отелей:')
        else:
            if int(message) not in range(1, LIMIT + 1):
                send_message(chat_id, f'Разрешено выводить не более {LIMIT} отелей.\n'
                                        f'Введите количество отелей:')
                return False
            else:
                users_dict[chat_id].limit = int(message)
                # print(users_dict[chat_id].limit)
                return True
    except ValueError:
        send_message(chat_id, 'Введите ЧИСЛО отелей:')


def get_user_photo_limit(chat_id, message, message_id=None, step=False) -> bool:
    try:
        if not step:
            edit_message_button(chat_id, message_id, message)
            send_message(chat_id, 'Сколько фотографий вы хотите загрузить?')
        else:
            if int(message) not in range(1, LIMIT + 1):
                send_message(chat_id, f'Разрешено загружать не более {LIMIT} фото.\n'
                                      f'Введите количество фотографий:')
                return False
            else:
                users_dict[chat_id].photo_limit = int(message)
                # print(users_dict[chat_id].limit)
                return True
    except ValueError:
        send_message(chat_id, 'Введите ЧИСЛО фотографий:')


def get_user_part_world(chat_id, message, message_id=None, step=False):
    if not step:
        text = 'В какой части света ищем?'
        button_list = []
        for part in WORLD_PART:
            button = {'text': f"{part['name']}", 'callback_data': f"{part['name']}"}
            button_list.append([button])
        inline_keyboard(chat_id, sorted(button_list, key=lambda x: x[0]['text']), text)
    else:
        for part in WORLD_PART:
            if part['name'] == message:
                users_dict[chat_id].part = message
                edit_message_button(chat_id, message_id, f'Часть света: {message}')
                return True
        return False
        # print(users_dict[chat_id].part)


def get_user_country(chat_id, user_world_part, message_id=None, step=False):
    if not step:
        text = 'В какой стране ищем?'
        button_list = []
        for part in WORLD_PART:
            if part['name'] == user_world_part:
                for country in part['countries']:
                    button = {'text': f"{DATA[country]['name']}", 'callback_data': f"{country}"}
                    button_list.append(button)
                break

        button_list = sorted(button_list, key=lambda x: x['text'])
        if not len(button_list) // 2:
            button_list_result = [[button_list[x], button_list[x + 1]] for x in range(0, len(button_list), 2)]
        else:
            button_list_result = [[button_list[x], button_list[x + 1]] for x in range(0, len(button_list) - 1, 2)]
            button_list_result.append([button_list[-1]])

        inline_keyboard(chat_id, button_list_result, text)
    else:
        try:
            users_dict[chat_id].locale = DATA[int(user_world_part)]['hcomLocale']
            # print(users_dict[chat_id].locale)
            edit_message_button(chat_id, message_id, f'Страна: {DATA[int(user_world_part)]["name"]}')
            return True
        except ValueError:
            return False


def town_search(chat_id, message=None, message_id=None, step=False):
    if not step:
        town_name = users_dict[chat_id].town
        locale = users_dict[chat_id].locale

        response = search_town(town_name, locale)

        button_list = []

        for group in response['suggestions']:
            if group['group'] == 'CITY_GROUP':
                for town in group['entities']:
                    if town['type'] == 'CITY':
                        full_name = re.sub(r'<.*?>', '', town['caption'])
                        button_list.append([{'text': f"{full_name}",
                                            'callback_data': f"{town['destinationId']}"}])
                break

        if len(button_list) > 0:
            inline_keyboard(chat_id, button_list, 'Уточните город:')
        else:
            raise SearchTownError('Такой город не найден... Попробуйте ввести его заново.')
    else:
        users_dict[chat_id].town_id = message[0]
        # print(users_dict[chat_id].locale)
        edit_message_button(chat_id, message_id, f'Точное название города:\n{message[1]}')
        return True
    return False


def output_pattern(rating, name, address, date_in, date_out, cost, link):
    if 'streetAddress' not in address:
        street = ''
    else:
        street = address['streetAddress']

    full_address = f"{address['countryName']}, {address['locality']}, {street}"
    days = (date_out - date_in).days
    date_in=date_in.strftime('%d.%m.%Y')
    date_out=date_out.strftime('%d.%m.%Y')

    struct = f"Рейтинг: {rating}\n" \
             f"Отель: {name}\n" \
             f"Адрес: {full_address}\n" \
             f"Дата заезда-выезда: {date_in} - {date_out}, всего {days} дней\n" \
             f"Цена за сутки: {cost}$\n" \
             f"Цена за {days} суток: {round(cost * days, 2)}$\n" \
             f"Ссылка на страницу: https://ru.hotels.com/ho{link}"

    return struct


def hostel_search(chat_id, sort_mode):
    send_message(chat_id, 'Начинаю поиск...')

    town_id = users_dict[chat_id].town_id
    page_size = users_dict[chat_id].limit
    date_in = users_dict[chat_id].date_in
    date_out = users_dict[chat_id].date_out
    locale = users_dict[chat_id].locale
    photo_limit = users_dict[chat_id].photo_limit

    try:
        response = search_hostels(id=town_id,
                                  page_size=page_size,
                                  date_in=date_in.strftime('%Y-%m-%d'),
                                  date_out=date_out.strftime('%Y-%m-%d'),
                                  locale=locale, sort_mode=sort_mode)

        for hostel in response['data']['body']['searchResults']['results']:
            message = output_pattern(rating=hostel['starRating'],
                                     name=hostel['name'],
                                     address=hostel['address'],
                                     date_in=date_in,
                                     date_out=date_out,
                                     cost=hostel['ratePlan']['price']['exactCurrent'],
                                     link=hostel['id'])

            if isinstance(photo_limit, int):
                response_photo = search_photo(hostel['id'])['hotelImages'][:photo_limit]

                if photo_limit > 1:
                    photo_list = []
                    for index in range(photo_limit):
                        photo_link = re.sub(r'_{size}', '', response_photo[index]['baseUrl'])
                        photo_list.append({'type': 'photo', 'media': photo_link})

                    photo_list[0]['caption'] = message

                    a = send_media_group(chat_id, json.dumps(photo_list)).json()
                    print()
                else:
                    photo = re.sub(r'_{size}', '', response_photo[0]['baseUrl'])
                    send_photo(chat_id, photo, message)
            else:
                send_message(chat_id, link_mode=True, text=message)

    except Exception as error:
        print(f'{type(error).__name__}: {error}')
        raise SearchHostelError('Что-то пошло не так... Попробуйте заново')
