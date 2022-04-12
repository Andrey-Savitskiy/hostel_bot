import requests


URL = 'https://hotels4.p.rapidapi.com/'

HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': "44e957bd76msh37ab38f858b52b6p1dc1e1jsn3a06b9c2e19b"
}


def get_meta_data():
    with open('meta_data.py', 'a', encoding='utf-8') as file:
        request = requests.request("GET", URL + 'get-meta-data', headers=HEADERS)
        counter = 0
        file.write('DATA = {\n')

        for line in list(request.text[2:-2].split('},{')):
            result = f"\t{counter}: {{"

            for item in line.split(','):
                key = item.split(':')[0][1:-1]
                value = item.split(':')[1][1:-1]
                result += f"'{key}': '{value}', "

            file.write(result[:-2] + '},\n')
            counter += 1
        file.write('}\n')


def search_town(name_town, locale):
    querystring = {"query": name_town, "locale": locale}
    response = requests.request("GET", URL + 'locations/v2/search', headers=HEADERS, params=querystring)
    return response.json()


def search_hostels(id, page_size, date_in, date_out, locale, sort_mode):
    querystring = {"destinationId": id,
                   "pageNumber": "1", "pageSize": page_size,
                   "checkIn": date_in, "checkOut": date_out,
                   "adults1": "1", "sortOrder": sort_mode,
                   "locale": locale, "currency": "USD"}
    response = requests.request("GET", URL + 'properties/list', headers=HEADERS, params=querystring)
    return response.json()


def search_photo(hostel_id):
    querystring = {"id": hostel_id}
    response = requests.request("GET", URL + 'properties/get-hotel-photos',
                                headers=HEADERS, params=querystring)
    return response.json()
