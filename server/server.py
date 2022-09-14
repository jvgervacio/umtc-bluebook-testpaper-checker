from flask import Flask, request
from flask_restful import Api, Resource


_APP, _API = None, None

def initialize():
    _APP = Flask(__name__)
    _API = Api(_APP)

if __name__ == '__main__':
    initialize()
    _APP.run()