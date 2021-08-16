import requests
from pprint import pprint

with open('token.txt', 'r', encoding='utf-8') as token_file:
    access_token = token_file.read()

with open('token_yandex_drive.txt', 'r', encoding='utf-8') as token_yandex_drive_file:
    token_yandex_drive = token_yandex_drive_file.read()

API_BASE_URL_VK = 'https://api.vk.com/method/'
API_BASE_URL_YANDEX_DRIVE = 'https://cloud-api.yandex.net/v1/disk/resources/upload'


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
    for photo in photo_dict:
        photo_name_and_url = {}
        if photo['likes'] not in photo_names:
            photo_name_and_url['photo_name'] = str(photo['likes'])
            photo_names.append(photo['likes'])
        else:
            photo_name_and_url['photo_name'] = f"{photo['likes']}, {photo['date']}"
        photo_name_and_url['url'] = photo['sizes']['url']
        photo_for_upload.append(photo_name_and_url)

    headers_yandex_drive = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_yandex_drive}'}

    for uploading_photo in photo_for_upload:
        name_photo = uploading_photo['photo_name']
        photo_url = uploading_photo['url']
        params_yandex_drive = {'path': 'backup_vk/' + name_photo,
                           'overwrite': 'true',
                           'url': photo_url}
        requests.post(API_BASE_URL_YANDEX_DRIVE, headers=headers_yandex_drive, params=params_yandex_drive)
        print(f'Файл {name_photo} добавлен на Яндекс.диск')


def main_menu(command):
    if command == 'add':
        photos = get_photos_for_backup(int(input('Введите id аккаунта пользователя в ВКонтакте: ')))
        upload_photo(photos)


main_menu(input('Введите команду: '))
# upload = requests.get(response.json()['href'], headers=headers_yandex_drive)
#
# print(upload)
# print(upload.json())
# 552934290