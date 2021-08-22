import requests
import json
from datetime import datetime
from pprint import pprint

with open('token.txt', 'r', encoding='utf-8') as token_file:
    access_token = token_file.read()

with open('token_yandex_drive.txt', 'r', encoding='utf-8') as token_yandex_drive_file:
    token_yandex_drive = token_yandex_drive_file.read()

API_BASE_URL_VK = 'https://api.vk.com/method/'
API_BASE_URL_YANDEX_DRIVE = 'https://cloud-api.yandex.net/v1/disk/'


def get_photos_for_backup(owner_id, count=5):
    params = {
        'v': '5.131',
        'owner_id': owner_id,
        'album_id': 'profile',
        'access_token': access_token,
        'rev': 1,
        'extended': 1,
        'count': count
    }

    photo_full_information = requests.get(API_BASE_URL_VK + 'photos.get', params=params)
    photo_list = photo_full_information.json()['response']['items']
    photo_information = []

    for photo in photo_list:
        photo_inf = {'likes': photo['likes']['count'], 'date': photo['date'], 'sizes': photo['sizes'][-1]}
        photo_information.append(photo_inf)
    return photo_information


def upload_photo(photo_dict):
    photo_for_upload = []
    photo_names = []
    photo_inf_for_result_file = []
    for photo in photo_dict:
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


def delete():
    params = {'path': 'backup_vk'}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_yandex_drive}'
    }
    files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)
    pprint(files_info.json())

    for file_name in files_info.json()['_embedded']['items']:
        print(file_name['path'])
        params = {
            'path': file_name['path'],
            'permanently': True
        }

        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token_yandex_drive}'
        }

        requests.delete(API_BASE_URL_YANDEX_DRIVE + 'resources/', params=params, headers=headers)
        print(f"Файл '{file_name['name']}' удален.")


def delete_photo_in_folder():
    with open('result.json', 'r') as result_file:
        uploaded_photos = json.load(result_file)
        for photo in uploaded_photos:
            params = {
                'path': 'backup_vk/' + photo['file_name'],
                'permanently': True
            }

            headers = {
                'Accept': 'application/json',
                'Authorization': f'OAuth {token_yandex_drive}'
            }

            requests.delete(API_BASE_URL_YANDEX_DRIVE + 'resources/', params=params, headers=headers)
            print(f"Файл '{photo['file_name']}' удален.")
        new_result_file = []
        for photo in new_result_file:
            if photo not in uploaded_photos:
                new_result_file.append(photo)
    with open('result.json', 'w') as del_file:
        json.dump(new_result_file, del_file, indent=2)  #


def show_photo():
    print('Список загруженных файлов:')
    with open('result.json', 'r') as result_file:
        uploaded_photo_list = json.load(result_file)
        for photo in uploaded_photo_list:
            print(f"Имя файла: {photo['file_name']}  Тип файла: {photo['type']}")


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
            photo = get_photos_for_backup(input_id, quantity_photo_int)
            print(f"Загрузка {quantity_photo_int} фото ...")
        except ValueError:
            photo = get_photos_for_backup(input_id)
            print('Загрузка по умолчанию 5 фото ...')
        upload_photo(photo)

    elif main_command == 'del':
        delete()

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


# 552934290
# 25222915