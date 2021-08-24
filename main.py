import requests
import json
from datetime import datetime
from pprint import pprint

with open('welcome.txt', 'r', encoding='utf-8') as welcome_file:
    print(welcome_file.read())

with open('token.txt', 'r', encoding='utf-8') as token_file:
    access_token = token_file.read()

with open('token_yandex_drive.txt', 'r', encoding='utf-8') as token_yandex_drive_file:
    token_yandex_drive = token_yandex_drive_file.read()

API_BASE_URL_VK = 'https://api.vk.com/method/'
API_BASE_URL_YANDEX_DRIVE = 'https://cloud-api.yandex.net/v1/disk/'


def upload_photo(owner_id, count=5):
    params_for_get_albums = {
        'v': '5.131',
        'owner_id': owner_id,
        'access_token': access_token,
    }

    albums_information = requests.get(API_BASE_URL_VK + 'photos.getAlbums', params=params_for_get_albums)
    dict_for_select_album = {1: 'profile', 2: 'wall'}
    print('Список альбомов для загрузки:')
    print('1 - Фотографии профиля\n2 - Фотографии со стены')
    album_count = 2
    for album in albums_information.json()['response']['items']:
        album_count += 1
        dict_for_select_album[album_count] = album['id']
        print(f"{album_count} - {album['title']}")
    print(f"{album_count+1} - Выход")
    dict_for_select_album[album_count+1] = 0

    try:
        select_album_number = int(input('Введите номер альбома: '))
        selected_album = dict_for_select_album[select_album_number]

        if selected_album == 0:
            return False
    except ValueError:
        print('Неверное значение.')
        return False

    params_for_get_photos = {
        'v': '5.131',
        'owner_id': owner_id,
        'album_id': selected_album,
        'access_token': access_token,
        'rev': 1,
        'extended': 1,
        'count': count
    }

    photo_full_information = requests.get(API_BASE_URL_VK + 'photos.get', params=params_for_get_photos)
    try:
        photo_list = photo_full_information.json()['response']['items']
        photo_information = []
        for photo in photo_list:
            photo_inf = {'likes': photo['likes']['count'], 'date': photo['date'], 'sizes': photo['sizes'][-1]}
            photo_information.append(photo_inf)

        photo_for_upload = []
        photo_names = []
        photo_inf_for_result_file = []

        for photo in photo_information:
            photo_name_and_url = {}
            photo_name_and_size_for_result_file = {}
            if photo['likes'] not in photo_names:
                photo_name_and_url['photo_name'] = str(photo['likes'])
                photo_name_and_size_for_result_file['file_name'] = str(photo['likes'])
                photo_names.append(photo['likes'])
            else:
                photo_name_and_url['photo_name'] = \
                    f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"
                photo_name_and_size_for_result_file['file_name'] = \
                    f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"
            photo_name_and_url['url'] = photo['sizes']['url']
            photo_name_and_url['type'] = photo['sizes']['type']
            photo_for_upload.append(photo_name_and_url)
            photo_name_and_size_for_result_file['type'] = photo['sizes']['type']
            photo_inf_for_result_file.append(photo_name_and_size_for_result_file)

        headers_yandex_drive = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token_yandex_drive}'}

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

        with open('result.json', 'w') as result_file:
            json.dump(photo_inf_for_result_file, result_file, indent=2)
    except KeyError:
        print('Такой страницы не существует, либо отсутствует доступ.')
        return False


def delete_photo():
    params = {'path': 'backup_vk'}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_yandex_drive}'
    }
    files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)

    for file_name in files_info.json()['_embedded']['items']:

        params = {
            'path': file_name['path'],
            'permanently': True
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token_yandex_drive}'
        }

        requests.delete(API_BASE_URL_YANDEX_DRIVE + 'resources/', params=params, headers=headers)

        with open('result.json', 'w') as del_file:
            json.dump(obj=[], fp=del_file, indent=2)
        print(f"Файл '{file_name['name']}' удален.")


def show_photo():
    print('Список загруженных файлов:')
    params = {'path': 'backup_vk'}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_yandex_drive}'
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

    else:
        print('Неизвестная команда.\nДля справки введите "help".')


while True:
    command = input('Введите команду: ')
    if command == 'exit':
        print('Работа завершена.')
        break
    else:
        main_menu(command)
