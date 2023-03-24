import requests
from config import YANDEX_TOKEN, API_BASE_URL_YANDEX_DRIVE

def upload_to_yandex(photo_list, count):

    response = requests.put(
        API_BASE_URL_YANDEX_DRIVE + 'resources/',
        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {YANDEX_TOKEN}'
        },
        params = {
            'path': 'backup_vk'
        }
    )

    print(f"Загрузка {count} фото ...")

    for uploading_photo in photo_list:
        name_photo = uploading_photo['photo_name']
        photo_url = uploading_photo['url']

        requests.post(
            API_BASE_URL_YANDEX_DRIVE + 'resources/upload',
            headers = {
                'Accept': 'application/json',
                'Authorization': f'OAuth {YANDEX_TOKEN}'
            },
            params = {
                'path': 'backup_vk/' + name_photo,
                'overwrite': 'true',
                'url': photo_url,
            },
        )

        print(f'Файл {name_photo} добавлен на Яндекс.Диск')
