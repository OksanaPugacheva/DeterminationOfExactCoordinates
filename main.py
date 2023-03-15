import click
from dadata import Dadata
from user_settings import create_table, get_settings, settings_ex, delete_table, update_lung


def input_num(max_num, prompt=None):
    while True:
        s = input(prompt)
        if s.isdigit() and 1 <= int(s) <= max_num:
            return s
        else:
            print(f'Необходимо ввести число от 1 до {max_num}')


def exact_coordinates(address, api_key, secret_key, language):
    try:
        values = []
        dadata = Dadata(api_key, secret_key)
        result = dadata.suggest("address", address, language=language)
        address_num = 0
        if result:
            for i in result:
                address_num = address_num + 1
                values.append(i['value'])
                print(f"{address_num} -> {i['value']}")

            y = input_num(address_num, 'Введите номер подходящего адреса:\n>>')
            a = int(y)
            result_clean = dadata.suggest("address", values[a - 1], language=language, count=1)
            return result_clean[0]
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
        api_key = input('Введите ключ api:\n>>')
        secret_key = input('Введите секретный ключ:\n>>')
        language = input('Выберите язык ru или en:\n>>')
        create_table(api_key, secret_key, language)
    elif settings_ex() == 1 and (setting_lung == 'ru' or setting_lung == 'en'):
        update_lung(setting_lung)

    actual_setting = get_settings()
    api_key = actual_setting[0][0]
    secret_key = actual_setting[0][1]
    language = actual_setting[0][2]

    while True:
        address = input('Введите адрес:\n>>')
        exact_coord = exact_coordinates(address, api_key, secret_key, language)
        if exact_coord:
            lat = exact_coord["data"]["geo_lat"]
            lon = exact_coord["data"]["geo_lon"]
            if lat and lon:
                print(f'{exact_coord["value"]}: {lat} ш. {lon} д.')
            else:
                print('Точные координаты места неизвестны')
        else:
            print('По данному запросу ничего не нашлось')


if __name__ == "__main__":
    main()