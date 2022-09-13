import json

_JSON_FILE_NAME = "./database/data.json"

def load_json():
    try:
        with open(_JSON_FILE_NAME, 'r') as file:
            return json.load(file, )
    except json.JSONDecodeError as ex:
        print(f'[ERROR] Failed loading json file "{_JSON_FILE_NAME}"', ex)
        return None

def save_json(json_data: dict()):
    with open(_JSON_FILE_NAME, 'w') as file:
        json.dump(json_data, file)

if __name__ == '__main__':
    pass