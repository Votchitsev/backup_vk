import requests
from config import API_BASE_URL_VK, VK_TOKEN

def vk_get_albums(owner_id, count):
    vk_albums = requests.get(
        API_BASE_URL_VK + 'photos.getAlbums', 
        params = {
        'v': '5.131',
        'owner_id': owner_id,
        'access_token': VK_TOKEN,
        'need_system': '1'
        }
    )

    vk_albums = vk_albums.json()

    if "error" in vk_albums:
        print(
            f"Ошибка {vk_albums['error']['error_code']}: "
            f"{vk_albums['error']['error_msg']}")
        
        return False
    
    print('Список альбомов для загрузки: ')
    
    result = {}

    album_count = 0

    for album in vk_albums['response']['items']:
        album_count += 1
        result[album_count] = album['id']
        print(f"{album_count} - {album['title']}")
        
    print(f"{album_count + 1} - Выход")

    return result