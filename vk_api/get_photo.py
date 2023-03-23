import requests
from config import API_BASE_URL_VK, VK_TOKEN

def vk_get_photo(owner_id, album_id, count):
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