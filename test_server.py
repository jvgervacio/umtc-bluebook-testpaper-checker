from flask import Flask, make_response, jsonify
from flask_socketio import SocketIO, emit, send
async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)

@app.route("/")
def index():
    return make_response(jsonify({'data':100 }), 200)

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    
@socketio.on('hello')
def hello(args):
    print(args)
    emit("hi", {"data": 123})

if __name__ == '__main__':
    socketio.run(app, debug=False, host= "0.0.0.0")