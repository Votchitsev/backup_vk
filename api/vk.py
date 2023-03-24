import requests
from config import API_BASE_URL_VK, VK_TOKEN

def get_albums(owner_id):

    albums = requests.get(
        API_BASE_URL_VK + 'photos.getAlbums', 
        params = {
        'v': '5.131',
        'owner_id': owner_id,
        'access_token': VK_TOKEN,
        'need_system': '1'
        }
    )

    albums = albums.json()

    if "error" in albums:
        print(
            f"Ошибка {albums['error']['error_code']}: "
            f"{albums['error']['error_msg']}")
        
        return False
    
    print('Список альбомов для загрузки: ')
    
    result = {}

    album_count = 0

    for album in albums['response']['items']:
        album_count += 1
        result[album_count] = album['id']
        print(f"{album_count} - {album['title']}")
        
    print(f"{album_count + 1} - Выход")

    return result


def get_photo(owner_id, album_id, count):

    response = requests.get(
        API_BASE_URL_VK + 'photos.get',
        params = {
            'v': '5.131',
            'owner_id': owner_id,
            'album_id': album_id,
            'access_token': VK_TOKEN,
            'rev': 1,
            'extended': 1,
            'count': count
        })

    response = response.json()
    
    if "error" in response.keys():
        print(f"Ошибка {response['error']['error_code']}: "
              f"{response['error']['error_msg']}")
        
        return False

    photo_list = response['response']['items']

    result = [
        {
        'likes': photo['likes']['count'],
        'date': photo['date'],
        'sizes': photo['sizes'][-1]
        } for photo in photo_list
    ]
    
    return result
