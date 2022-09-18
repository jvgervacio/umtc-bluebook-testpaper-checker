import json
from random import randint
from models.student import Student

_JSON_FILE_NAME = "database/data.json"


def load():
    try:
        with open(_JSON_FILE_NAME, 'r') as file:
            return json.load(file,)
    except json.JSONDecodeError as ex:
        print(f'[ERROR] Failed loading json file "{_JSON_FILE_NAME}"', ex)
        return None

def commit(data: dict = None):
    with open(_JSON_FILE_NAME, 'w') as file:
        json.dump(data, file)

def get_session_id() -> int:
    data = load()
    return data['session_id']

def set_answer_key(ans_key: list):
    data = {'session_id':  randint(0, 999999),
            'answer_key': ans_key,
            'students': []}

    commit(data)

def get_answer_key() -> list:
    data = load()
    return data['answer_key']

def add_student(student: Student):
    data = load()
    data['students'].append(student.serialize())
    commit(data)

def get_students() -> list:
    data = load()
    return data['students']

def clear():
    data = {}
    commit(data)

