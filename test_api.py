import main


def test():
    print('\nПроверка загрузки фото с тестовой страницы без возможности выбора альбома...\n')
    main.upload_photo(6581785)
    print('\nЗагрузка фото с несуществующей страницы...\n')
    main.upload_photo(2, 10)
    print('\nЗагрузка фото со страницы Павла Дурова с возможностью выбора альбома...\n')
    main.upload_photo(1, 1)
    print('\nПросмотр загруженных файлов...\n')
    main.show_photo()
    print('\nУдаление загруженных файлов...\n')
    main.delete_photo()
