from builtins import input

import requests
import json
from datetime import datetime
from pprint import pprint

# with open('welcome.txt', 'r', encoding='utf-8') as welcome_file:
#     print(welcome_file.read())

with open('token.txt', 'r', encoding='utf-8') as token_file:
    access_token = token_file.read()

with open('token_yandex_drive.txt', 'r', encoding='utf-8') as token_yandex_drive_file:
    token_yandex_drive = token_yandex_drive_file.read()

API_BASE_URL_VK = 'https://api.vk.com/method/'
API_BASE_URL_YANDEX_DRIVE = 'https://cloud-api.yandex.net/v1/disk/'


class Vkontakte:
    def __init__(self, owner_id, count=5):
        self.owner_id = owner_id
        self.token = access_token
        self.count = count

    def get_album_list(self):
        params = {
            'v': '5.131',
            'owner_id': self.owner_id,
            'access_token': self.token,
            'need_system': '1'
        }

        album_list = requests.get(API_BASE_URL_VK + 'photos.getAlbums', params=params)

        try:
            album_name_list = {}
            for item in album_list.json()['response']['items']:
                album_name_list[item['title']] = item['id']
            return album_name_list
        except KeyError:
            print(f"Ошибка: {album_list.json()['error']['error_msg']}")
            return False

    def select_photo(self):
        album_numbers = {}
        album_count = 0
        if not self.get_album_list:
            pass
        try:
            for i in self.get_album_list().values():
                album_count += 1
                album_numbers[album_count] = i

            print(album_numbers)
            print('Выдерите фото для загрузки: ')
            number = 0
            for albums in self.get_album_list():
                number += 1
                print(f'{number} {albums}')
            selected_album = int(input('Введите номер альбома, из которого хотите загрузить фото: '))
            return album_numbers[selected_album]
        except KeyError:
            print(self.get_album_list['error']['error_msg'])

    def upload_photo(self):
        params = {
            'v': '5.131',
            'owner_id': self.owner_id,
            'album_id': self.select_photo(),
            'access_token': self.token,
            'rev': 1,
            'extended': 1,
            'count': self.count
        }
        full_photo_information = requests.get(API_BASE_URL_VK + 'photos.get', params=params)
        photo_list = full_photo_information.json()['response']['items']
        photo_information = []
        for photo in photo_list:
            photo_inf = {'likes': photo['likes']['count'], 'date': photo['date'], 'sizes': photo['sizes'][-1]}
            photo_information.append(photo_inf)

        photo_for_upload = []
        photo_names = []

        for photo in photo_information:
            inf_for_upload_and_result = {}
            if photo['likes'] not in photo_names:
                inf_for_upload_and_result['file_name'] = str(photo['likes'])
                photo_names.append(photo['likes'])
            else:
                inf_for_upload_and_result['file_name'] = \
                    f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"
            inf_for_upload_and_result['url'] = photo['sizes']['url']
            inf_for_upload_and_result['size'] = photo['sizes']['type']
            photo_for_upload.append(inf_for_upload_and_result)
        return photo_for_upload


class Yandex:
    def __init__(self, files):
        self.files = files
        self.token = token_yandex_drive
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {token_yandex_drive}'
        }

    def upload_photo(self):
        file_list = self.files
        print(f"Загрузка {user.count} фото ...")
        for uploading_photo in file_list:
            name_photo = uploading_photo['file_name']
            photo_url = uploading_photo['url']
            upload_params = {
                'path': 'backup_vk/' + name_photo,
                'overwrite': 'true',
                'url': photo_url
            }

            requests.post(API_BASE_URL_YANDEX_DRIVE + 'resources/upload',
                          headers=self.headers,
                          params=upload_params)
            print(f'Файл {name_photo} добавлен на Яндекс.Диск')
        inf_for_result_file = []
        for i in file_list:
            photo_inf = {'file_name': i['file_name'], 'size': i['size']}
            inf_for_result_file.append(photo_inf)

        with open('result.json', 'r') as result_file:
            if json.load(result_file) == "empty":
                with open('result.json', 'w') as new_result_file:
                    json.dump(inf_for_result_file, new_result_file, indent=2)
            else:
                with open('result.json', 'r') as new_result_file:
                    data = json.load(new_result_file)
                with open('result.json', 'w') as new_result_file:
                    for photo in inf_for_result_file:
                        data.append(photo)
                    json.dump(data, new_result_file, indent=2)

    def delete_photo(self):
        params = {'path': 'backup_vk'}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
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
                json.dump(obj='empty', fp=del_file, indent=2)
            print(f"Файл '{file_name['name']}' удален.")


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
            user = Vkontakte(owner_id=input_id, count=quantity_photo_int)
            files = user.upload_photo()
            cloud = Yandex(files=files)
            cloud.upload_photo()
        except ValueError:
            user = Vkontakte(owner_id=input_id)
            files = user.upload_photo()
            cloud = Yandex(files=files)
            cloud.upload_photo()
    elif main_command == 'del':
        delete_photo()

    elif main_command == 'help':
        with open('help.txt', 'r', encoding='utf-8') as help_file:
            print(help_file.read())

    elif main_command == 'show':
        show_photo()

    elif main_command == 'test':
        assert upload_photo(552934290, 5)

    else:
        print('Неизвестная команда.\nДля справки введите "help".')


while True:
    command = input('Введите команду: ')
    if command == 'exit':
        print('Работа завершена.')
        break
    else:
        main_menu(command)


# test = Vkontakte('552934290')

user = Vkontakte('25222915')

cloud = Yandex()
# test_2 = Vkontakte('3')
#
# while True:
#     command = input('Введите команду: ')
#     if command == 'exit':
#         print('Работа завершена.')
#         break
#     else:
#         main_menu(command)

# pprint(test.get_album_list())
# pprint(sasha.get_album_list())
# pprint(user.upload_photo())
cloud.delete_photo()

# print(test.get_album_list())

# This is old code_____________________________

#     def upload_photo(self, count=5):
#         params_for_get_albums = {
#             'v': '5.131',
#             'owner_id': owner_id,
#             'access_token': access_token
#         }
#
#     albums_information = requests.get(API_BASE_URL_VK + 'photos.getAlbums', params=params_for_get_albums)
#
#     dict_for_select_album = {1: 'profile', 2: 'wall'}
#     try:
#         albums_information.json()['response']['items'] = True
#         print('Список альбомов для загрузки:\n1 - Фотографии профиля\n2 - Фотографии со стены')
#         album_count = 2
#         for album in albums_information.json()['response']['items']:
#             album_count += 1
#             dict_for_select_album[album_count] = album['id']
#             print(f"{album_count} - {album['title']}")
#         print(f"{album_count + 1} - Выход")
#         dict_for_select_album[album_count + 1] = 0
#     except KeyError:
#
#
#     try:
#         select_album_number = int(input('Введите номер альбома: '))
#         selected_album = dict_for_select_album[select_album_number]
#
#         if selected_album == 0:
#             return False
#     except ValueError:
#         print('Неверное значение.')
#         return False
#
#     params_for_get_photos = {
#         'v': '5.131',
#         'owner_id': owner_id,
#         'album_id': selected_album,
#         'access_token': access_token,
#         'rev': 1,
#         'extended': 1,
#         'count': count
#     }
#
#     photo_full_information = requests.get(API_BASE_URL_VK + 'photos.get', params=params_for_get_photos)
#     try:
#         photo_list = photo_full_information.json()['response']['items']
#         photo_information = []
#         for photo in photo_list:
#             photo_inf = {'likes': photo['likes']['count'], 'date': photo['date'], 'sizes': photo['sizes'][-1]}
#             photo_information.append(photo_inf)
#
#         photo_for_upload = []
#         photo_names = []
#         photo_inf_for_result_file = []
#
#         for photo in photo_information:
#             photo_name_and_url = {}
#             photo_name_and_size_for_result_file = {}
#             if photo['likes'] not in photo_names:
#                 photo_name_and_url['photo_name'] = str(photo['likes'])
#                 photo_name_and_size_for_result_file['file_name'] = str(photo['likes'])
#                 photo_names.append(photo['likes'])
#             else:
#                 photo_name_and_url['photo_name'] = \
#                     f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"
#                 photo_name_and_size_for_result_file['file_name'] = \
#                     f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"
#             photo_name_and_url['url'] = photo['sizes']['url']
#             photo_name_and_url['type'] = photo['sizes']['type']
#             photo_for_upload.append(photo_name_and_url)
#             photo_name_and_size_for_result_file['type'] = photo['sizes']['type']
#             photo_inf_for_result_file.append(photo_name_and_size_for_result_file)
#
#         headers_yandex_drive = {
#             'Accept': 'application/json',
#             'Authorization': f'OAuth {token_yandex_drive}'}
#
#         print(f"Загрузка {count} фото ...")
#
#         for uploading_photo in photo_for_upload:
#             name_photo = uploading_photo['photo_name']
#             photo_url = uploading_photo['url']
#             params_yandex_drive = {
#                 'path': 'backup_vk/' + name_photo,
#                 'overwrite': 'true',
#                 'url': photo_url
#             }
#             requests.post(API_BASE_URL_YANDEX_DRIVE + 'resources/upload',
#                           headers=headers_yandex_drive,
#                           params=params_yandex_drive)
#             print(f'Файл {name_photo} добавлен на Яндекс.Диск')
#
#         with open('result.json', 'r') as result_file:
#             if json.load(result_file) == "empty":
#                 with open('result.json', 'w') as new_result_file:
#                     json.dump(photo_inf_for_result_file, new_result_file, indent=2)
#             else:
#                 with open('result.json', 'r') as new_result_file:
#                     data = json.load(new_result_file)
#
#                 with open('result.json', 'w') as new_result_file:
#                     for photo in photo_inf_for_result_file:
#                         data.append(photo)
#                     json.dump(data, new_result_file, indent=2)
#
#     except KeyError:
#         print('Такой страницы не существует, либо отсутствует доступ.')
#         return False
#
#
# def delete_photo():
#     params = {'path': 'backup_vk'}
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': f'OAuth {token_yandex_drive}'
#     }
#     files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)
#
#     for file_name in files_info.json()['_embedded']['items']:
#
#         params = {
#             'path': file_name['path'],
#             'permanently': True
#         }
#
#         headers = {
#             'Accept': 'application/json',
#             'Authorization': f'OAuth {token_yandex_drive}'
#         }
#
#         requests.delete(API_BASE_URL_YANDEX_DRIVE + 'resources/', params=params, headers=headers)
#
#         with open('result.json', 'w') as del_file:
#             json.dump(obj='empty', fp=del_file, indent=2)
#         print(f"Файл '{file_name['name']}' удален.")
#
#
# def show_photo():
#     print('Список загруженных файлов:')
#     params = {'path': 'backup_vk'}
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': f'OAuth {token_yandex_drive}'
#     }
#
#     files_info = requests.get(API_BASE_URL_YANDEX_DRIVE + 'resources', params=params, headers=headers)
#     count = 0
#     for photo in files_info.json()['_embedded']['items']:
#         count += 1
#         pprint(f"{count}) Имя файла: {photo['name']} | Размер файла: {photo['size']}")
#
#
# def main_menu(main_command):
#     if main_command == 'add':
#         try:
#             input_id = int(input('Введите id аккаунта пользователя в ВКонтакте: '))
#         except ValueError:
#             print('Ошибка значения...')
#             return False
#
#         quantity_photo = input('Введите количество фото для загрузки (по умолчанию - 5): ')
#         try:
#             quantity_photo_int = int(quantity_photo)
#             upload_photo(input_id, quantity_photo_int)
#         except ValueError:
#             upload_photo(input_id)
#
#     elif main_command == 'del':
#         delete_photo()
#
#     elif main_command == 'help':
#         with open('help.txt', 'r', encoding='utf-8') as help_file:
#             print(help_file.read())
#
#     elif main_command == 'show':
#         show_photo()
#
#     elif main_command == 'test':
#         assert upload_photo(552934290, 5)
#
#     else:
#         print('Неизвестная команда.\nДля справки введите "help".')
#
#
# while True:
#     command = input('Введите команду: ')
#     if command == 'exit':
#         print('Работа завершена.')
#         break
#     else:
#         main_menu(command)
#
# # 552934290
#
#
