from sqlite3 import dbapi2
from flask_restful import Resource
import utils.database as db

class Student(Resource):
    def get(self, id):
        student = db.get_students()[id]
        return student