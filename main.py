import requests
from pprint import pprint

with open('token.txt', 'r', encoding='utf-8') as token_file:
    access_token = token_file.read()

API_BASE_URL = 'https://api.vk.com/method/'


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

    friends = requests.get(API_BASE_URL + 'photos.get', params=params)
    photo_list = friends.json()['response']['items']
    photo_dict = {}
    pprint(photo_list)
    for photo in photo_list:
        photos_size = {}
        size_list = []

        for url in photo['sizes']:
            photos_size[url['width']] = url['url']
            size_list.append(url['width'])

    # if photo_dict[photo['likes']['count']] in photo_dict:
    #      pass
    # else:
        photo_dict[photo['likes']['count']] = photos_size[size_list[-1]]

    return photo_dict


photos = get_photos_for_backup(6581785)

pprint(photos)
