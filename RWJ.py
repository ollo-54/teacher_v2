import json


def read_json(file_name):
    with open(file_name, 'r', encoding='utf8') as r_data:
        data_json = json.load(r_data)
    return data_json


def write_json(file_name, data_json):
    with open(file_name, 'w', encoding='utf8') as w_data:
        json.dump(data_json, w_data)







