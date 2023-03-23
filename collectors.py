from datetime import datetime


def collect_for_upload(photo_list):
    result = []
    names = []

    for photo in photo_list:
        d = {}

        if photo['likes'] not in names:
            d['photo_name'] = str(photo['likes'])
        else: 
            d['photo_name'] = f"{photo['likes']}_{datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')}"

        d['url'] = photo['sizes']['url']
        d['type'] = photo['sizes']['type']

        result.append(d)
    
    return result


def collect_for_write_file(photo_list):
    result = [
        {
        "file_name": photo["photo_name"],
        "type": photo["type"], 
        } for photo in photo_list
    ]

    return result
