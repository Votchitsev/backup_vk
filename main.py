from pprint import pprint
from api.vk import get_albums, get_photo
from api.yandex import upload_to_yandex, get_from_yandex, delete_from_yandex
from collect import collect_for_upload, collect_for_write_file
from file_manager import write_file, delete_files


def upload_photo(owner_id, count=5):

    albums = get_albums(owner_id)

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

    photo_information = get_photo(owner_id, selected_album, count)

    if not photo_information:
        return False

    photo_for_upload = collect_for_upload(photo_information)

    for_result_file = collect_for_write_file(photo_for_upload)

    upload_to_yandex(photo_for_upload, count)

    write_file(for_result_file)


def delete_photo():
    
    files = get_from_yandex()

    for file in files['_embedded']['items']:
        delete_from_yandex(file)

        print(f"Файл '{file['name']}' удален.")

    delete_files()
    

def show_photo():

    print('Список загруженных файлов:')

    files = get_from_yandex()

    count = 0

    for photo in files['_embedded']['items']:

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
