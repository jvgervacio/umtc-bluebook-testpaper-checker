from flask import Flask, request, jsonify, abort, make_response, Response,  render_template_string
from flask_restful import Api
from database import database as db
import cv2 as cv

app = Flask(__name__)
api = Api(app)

SESSION_ID = '123456'

logged_in = set()
cam = cv.VideoCapture(2)
@app.route('/answerkey/analysis/<int:item_no>')
def getItemAnalysis(item_no):
    if request.remote_addr not in logged_in:
        return abort(403)
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

@app.route('/answerkey')
def getAnswerKey():
    if request.remote_addr not in logged_in:
        return abort(403)
    ans_key = db.get_answer_key()
    return make_response(jsonify(ans_key), 200) 

@app.route('/students')
def getStudents():
    if request.remote_addr not in logged_in:
        return abort(403)
    students = db.get_students()
    if len(request.args) > 0:
        try:
            id = int(request.args.get('id'))
            make_response(jsonify(students[id]), 200) 
        except IndexError or ValueError:
            abort(404, "Student not found")

    return make_response(jsonify(students), 200) 

@app.route('/students/<int:id>')
def getStudent(id):
    if request.remote_addr not in logged_in:
        return abort(403)
    students= db.get_students()
    if id >= len(students):
        abort(404, 'student not found')
    return make_response(jsonify(students[id]), 200) 


@app.route('/logout', methods = ['POST'])
def logout():
    if request.remote_addr not in logged_in:
        return abort(401)
    while request.remote_addr in logged_in:
        logged_in.remove(request.remote_addr)

    return make_response("Success", 200)

@app.route('/auth', methods = ['POST'])
def autheticate():
    session_id = request.args.get('session')
    print(request.remote_addr, session_id)
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    else:
        logged_in.add(request.remote_addr)
    return 'success'
    
@app.route('/')
def index():
    # rendering webpage
    return render_template_string("video_feed.html")

def gen(camera):
    while True:
        success, frame = camera.read()
        # print(success)
        if not success:
            
            break
        else:
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@app.route('/video_feed')
def video_feed():
    
    return Response(gen(cam),mimetype='multipart/x-mixed-replace; boundary=frame')

def start(debug: bool = True):
    app.run(host = '0.0.0.0', 
            port = 5000, 
            debug = debug)

if __name__ == '__main__':
        start(True)