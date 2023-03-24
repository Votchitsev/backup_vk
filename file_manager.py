import json
import os

def write_file(data):
       
    file = open('result.json', 'r+')

    if os.stat('result.json').st_size == 0:
        json.dump(data, file, indent=2)
        file.close()

    else:
        previous_data = json.load(file)

        file.seek(0)
        file.close()
        
        file = open('result.json', 'w')

        for photo in data:
            previous_data.append(photo)
            json.dump(previous_data, file, indent=2)
