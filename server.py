from flask import Flask, request, jsonify, abort, make_response, Response,  render_template_string
from flask_restful import Api, Resource
from database import database as db
import cv2 as cv

app = Flask(__name__)
api = Api(app)

SESSION_ID = 123

@app.route('/<int:session_id>/answerkey/analysis/<int:item_no>')
def getItemAnalysis(session_id, item_no):
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    data = db.load()
    
    if item_no >= len(data['answer_key']) or item_no < 0:
        abort(401, 'Invalid Item Number')
    
    analysis = {
        'answer_key': data['answer_key'][item_no],
        'correct': 0,
        'wrong': 0,
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'E': 0,
    }
    for student in data['students']:
        ans = student['eval'][item_no]
        if len(ans) == 1:
            analysis[ans] += 1
            if ans == analysis['answer_key']:
                analysis['correct'] += 1
            else: analysis['wrong'] += 1
        else: analysis['wrong'] += 1

    return jsonify(analysis)

@app.route('/<int:session_id>/answerkey')
def getAnswerKey(session_id):
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    ans_key = db.get_answer_key()
    return jsonify(ans_key)

@app.route('/<int:session_id>/students')
def getStudents(session_id):
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    students = db.get_students()
    return jsonify(students)

@app.route('/<int:session_id>/students/<int:id>')
def getStudent(session_id, id):
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    students= db.get_students()
    if id >= len(students):
        abort(404, 'student not found')
    return jsonify(students[id])

@app.route('/auth', methods = ['POST'])
def autheticate():
    session_id = request.form.get('session_id', type=int)
    print(f'session_id: {session_id}')
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    return 'success'


@app.route('/')
def index():
    # rendering webpage
    return render_template_string('''
    <img id="bg" src="{{ url_for('video_feed') }}">
    ''')

def gen(camera):
    while True:
        #get camera frame
        ret, frame = camera.read()
        cv.imshow('live', frame)
        cv.waitKey(1)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@app.route('/video_feed')
def video_feed():
    cam = cv.VideoCapture(0, 2)
    return Response(gen(cam),mimetype='multipart/x-mixed-replace; boundary=frame')
def start(debug: bool = True):
    app.run(host = '0.0.0.0', 
            port = 5000, 
            debug = debug)

if __name__ == '__main__':
        start(True)