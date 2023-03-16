import click
from user_settings import create_table, get_settings, settings_ex, delete_table, update_lung
import re
import json
import requests


BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address'


def input_num(max_num, prompt=None):
    while True:
        s = input(prompt)
        if s.isdigit() and 0 <= int(s) <= max_num:
            return s
        else:
            print(f'Необходимо ввести число от 0 до {max_num}')


def suggest(query, api_key, language, count=10,):
    url = BASE_URL
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
        return res.json()
    elif res_status_code == 403:
        print('Несуществующий API-ключ или не подтверждена почта или исчерпан дневной лимит по количеству запросов')
        print('Удалить существующий API-ключ? Введите "да", чтобы удалить')
        if input('>>').lower() == 'да':
            delete_table()
            exit(0)
    else:
        print(f'При запросе к сервису dadata произошла ошибка {res_status_code}')
        exit(1)


def exact_coordinates(address, api_key, language):
    try:
        values = []
        result = suggest(address, api_key, language)
        address_num = 0
        if result:
            for i in result['suggestions']:
                address_num = address_num + 1
                values.append(i['value'])
                print(f"{address_num} -> {i['value']}")
            print(f"0 -> Нет нужного адреса")
            y = input_num(address_num, 'Введите номер подходящего адреса:\n>>')
            a = int(y)
            if a == 0:
                return 1
            else:
                result_clean = suggest(values[a - 1], api_key, language, count=1)
            return [result_clean['suggestions'][0]["value"], result_clean['suggestions'][0]['data']['geo_lat'],
                    result_clean['suggestions'][0]['data']['geo_lon']]
        else:
            return result
    except Exception as e:
        print(f'Ошибка: {e}')
        exit(1)


@click.command()
@click.option('--setting', default=1, help='--setting=0, чтобы заново заполнить все настройки')
@click.option('--setting_lung', type=click.Choice(['ru', 'en'], case_sensitive=False), help='изменить язык запроса')
def main(setting, setting_lung):
    """
    С помощью данного ПО вы можете узнать точные координаты введенного адреса.
    """
    if settings_ex() == 0 or setting == 0:
        delete_table()
        specific_char = re.compile(r'[^a-zA-Z0-9.]')
        while True:
            api_key = input('Введите ключ api:\n>>')
            if specific_char.search(api_key) or len(api_key) == 0:
                print("Api ключ может содержать только английские буквы и цифры, попробуйте снова")
            else:
                break
        language = input('Выберите язык ru или en:\n>>')
        if language != 'ru' and language != 'en':
            language = 'ru'
        create_table(api_key, language)
    elif settings_ex() == 1 and (setting_lung == 'ru' or setting_lung == 'en'):
        update_lung(setting_lung)

    actual_setting = get_settings()
    api_key = actual_setting[0][0]
    language = actual_setting[0][1]

    while True:
        address = input('Введите адрес:\n>>')
        exact_coord = exact_coordinates(address, api_key, language)
        if exact_coord == 1:
            print('Попробуйте уточнить запрос')
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
