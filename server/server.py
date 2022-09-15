from flask import Flask, request
from flask_restful import Api, Resource
from resources import Student

app = Flask(__name__)
api = Api(app)

def __init__():
    api.add_resource(Student, '/student/<int:id>')

def run(debug: bool = False):
    __init__()
    app.run(debug=debug)

if __name__ == '__main__':
    run()