import json

from models.student import Student

_JSON_FILE_NAME = "./database/data.json"
_DATA = {}

def load():
    try:
        with open(_JSON_FILE_NAME, 'r') as file:
            return json.load(file,)
    except json.JSONDecodeError as ex:
        print(f'[ERROR] Failed loading json file "{_JSON_FILE_NAME}"', ex)
        return None

def commit(data: dict = None):
    data = _DATA if data == None else data
    with open(_JSON_FILE_NAME, 'w') as file:
        json.dump(data, file)

def set_session_id(id: int):
        global _DATA
        _DATA = {'session_id': id,
                 'answer_key': [],
                 'students': []}
        commit()

def get_session_id() -> int:
        return _DATA['session_id']

def set_answer_key(ans_key: list):
        global _DATA
        _DATA['answer_key'] = ans_key
        commit()

def get_answer_key() -> list:
        return _DATA['answer_key']

def add_student(student: Student):
        global _DATA
        _DATA['students'].append(student.serialize())
        
if __name__ == '__main__':
    set_session_id(123)