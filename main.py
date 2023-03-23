import requests
import json
from datetime import datetime
from pprint import pprint

from config import API_BASE_URL_VK, API_BASE_URL_YANDEX_DRIVE, YANDEX_TOKEN
from vk_api.get_albums import vk_get_albums
from vk_api.get_photo import vk_get_photo
from collectors import collect_for_upload, collect_for_write_file


def upload_photo(owner_id, count=5):

    albums = vk_get_albums(owner_id, count)

    if albums:
        select_album_number = int(input('Введите номер альбома: '))
        selected_album = albums[select_album_number]

        if selected_album == 0:
            return False
        
        if selected_album not in albums.values():
            print('Неверное значение.')
            return False
            
    else:
        selected_album = 'profile'

    photo_information = vk_get_photo(owner_id, selected_album, count)

    if not photo_information:
        return False

    photo_for_upload = collect_for_upload(photo_information)

    photo_inf_for_result_file = collect_for_write_file(photo_for_upload)

    headers_yandex_drive = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {YANDEX_TOKEN}'}

    requests.put(API_BASE_URL_YANDEX_DRIVE + 'resources/',
                    headers=headers_yandex_drive,
                    params={'path': 'backup_vk'})

    print(f"Загрузка {count} фото ...")

    for uploading_photo in photo_for_upload:
        name_photo = uploading_photo['photo_name']
        photo_url = uploading_photo['url']
        params_yandex_drive = {
            'path': 'backup_vk/' + name_photo,
            'overwrite': 'true',
            'url': photo_url
        }
        requests.post(API_BASE_URL_YANDEX_DRIVE + 'resources/upload',
                        headers=headers_yandex_drive,
                        params=params_yandex_drive)
        print(f'Файл {name_photo} добавлен на Яндекс.Диск')

    with open('result.json', 'r') as result_file:
        if json.load(result_file) == "empty":
            with open('result.json', 'w') as new_result_file:
                json.dump(photo_inf_for_result_file, new_result_file, indent=2)
        else:
            with open('result.json', 'r') as new_result_file:
                data = json.load(new_result_file)

            with open('result.json', 'w') as new_result_file:
                for photo in photo_inf_for_result_file:
                    data.append(photo)
                json.dump(data, new_result_file, indent=2)


def delete_photo():
    params = {'path': 'backup_vk'}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {YANDEX_TOKEN}'
    }
    files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)

    for file_name in files_info.json()['_embedded']['items']:
        params = {
            'path': file_name['path'],
            'permanently': True
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {YANDEX_TOKEN}'
        }

        requests.delete(API_BASE_URL_YANDEX_DRIVE + 'resources/', params=params, headers=headers)

        with open('result.json', 'w') as del_file:
            json.dump(obj='empty', fp=del_file, indent=2)
        print(f"Файл '{file_name['name']}' удален.")


def show_photo():
    print('Список загруженных файлов:')
    params = {'path': 'backup_vk'}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {YANDEX_TOKEN}'
    }

    files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)
    count = 0
    for photo in files_info.json()['_embedded']['items']:
        count += 1
        pprint(f"{count}) Имя файла: {photo['name']} | Размер файла: {photo['size']}")


def main_menu(main_command):
    if main_command == 'add':
        try:
            input_id = int(input('Введите id аккаунта пользователя в ВКонтакте: '))
        except ValueError:
            print('Ошибка значения...')
            return False

        quantity_photo = input('Введите количество фото для загрузки (по умолчанию - 5): ')
        try:
            quantity_photo_int = int(quantity_photo)
            upload_photo(input_id, quantity_photo_int)
        except ValueError:
            upload_photo(input_id)

    elif main_command == 'del':
        delete_photo()

    elif main_command == 'help':
        with open('help.txt', 'r', encoding='utf-8') as help_file:
            print(help_file.read())

    elif main_command == 'show':
        show_photo()

    elif command == 'test':
        try:
            import test_api
            test_api.test()
        except NameError:
            print("Файл для тестирования не найден.")
            return False
    else:
        print('Неизвестная команда.\nДля справки введите "help".')


if __name__ == "__main__":
    with open('welcome.txt', 'r', encoding='utf-8') as welcome_file:
        print(welcome_file.read())

    while True:
        command = input('Введите команду: ').lower()
        if command == 'exit':
            print('Работа завершена.')
            break
        else:
            main_menu(command)
