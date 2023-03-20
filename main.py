import click
from user_settings import create_table, get_settings, settings_ex, update_lung, update_api
import re
import json
import requests


def input_num(max_num, prompt=None):
    while True:
        s = input(prompt)
        if s.isdigit() and 1 <= int(s) <= max_num:
            return int(s) - 1
        else:
            print(f'Необходимо ввести число от 1 до {max_num}')


def suggest(query, api_key, language, url, count=10):
    headers = {
        'Authorization': 'Token ' + api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'query': query,
        'count': count,
        'language': language
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    res_status_code = res.status_code
    if res_status_code == 200:
        return res.json()['suggestions']
    elif res_status_code == 403:
        print('Несуществующий API-ключ или не подтверждена почта или исчерпан дневной лимит по количеству запросов')
        print('Удалить существующий API-ключ? Введите "да", чтобы удалить. Нажмите enter, чтобы попробовать снова')
        if input('>>').lower() == 'да':
            update_api(get_api_key())
        return res_status_code
    else:
        print(f'При запросе к сервису dadata произошла ошибка {res_status_code}')
        exit(1)


def exact_coordinates(address, api_key, language, url):
    try:
        values = []
        result = suggest(address, api_key, language, url)
        address_num = 0
        if isinstance(result, list) and len(result) > 0:
            for i in result:
                address_num = address_num + 1
                values.append(i['value'])
                print(f"{address_num} -> {i['value']}")
            y = input_num(address_num, 'Введите номер подходящего адреса:\n>>')
            result_clean = suggest(values[y], api_key, language, url, count=1)
            return [result_clean[0]["value"], result_clean[0]['data']['geo_lat'],
                    result_clean[0]['data']['geo_lon']]
        else:
            return result
    except Exception as e:
        print(f'Ошибка: {e}')


def get_lung():
    language = input('Выберите язык ru или en:\n>>')
    if language != 'ru' and language != 'en':
        language = 'ru'
    return language


def get_api_key():
    specific_char = re.compile(r'[^a-zA-Z0-9.]')
    while True:
        api_key = input('Введите ключ api:\n>>')
        if specific_char.search(api_key) or len(api_key) == 0:
            print("Api ключ может содержать только английские буквы и цифры, попробуйте снова")
        else:
            break
    return api_key


@click.command()
def main():
    """
    С помощью данного ПО вы можете узнать точные координаты введенного адреса.
    """

    if settings_ex() == 0:
        create_table(get_api_key(), get_lung())

    print('Обновить ключ api введите: 1')
    print('Изменить язык введите: 2')
    print('Ввести запрос введите: нажмите enter')
    x = input('>>')
    if x == '2':
        update_lung(get_lung())
    elif x == '1':
        update_api(get_api_key())

    api_key, language, url = get_settings()

    while True:
        address = input('Введите адрес:\n>>')
        exact_coord = exact_coordinates(address, api_key, language, url)
        if exact_coord == 403:
            api_key = get_settings()[0]
        elif exact_coord:
            sd, lat, lon = exact_coord
            if lat and lon:
                print(f'{sd}: {lat} ш. {lon} д.')
            else:
                print('Точные координаты места неизвестны')
        else:
            print('По данному запросу ничего не нашлось')


if __name__ == "__main__":
    main()
