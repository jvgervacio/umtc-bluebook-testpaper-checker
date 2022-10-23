import mimetypes
from flask import Flask, request, jsonify, abort, make_response, Response,  send_file
from flask_restful import Api, reqparse
from database import database as db
import cv2 as cv
from threading import Thread
app = Flask(__name__)
api = Api(app)
import os
SESSION_ID = '123456'

logged_in = set()
cam = None
def initializeCamera():
    global cam
    cam = cv.VideoCapture(-1, cv.CAP_V4L2)
    cam.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)   

@app.route('/answerkey/analysis')
def getItemAnalysis():
    if request.remote_addr not in logged_in:
        return abort(403)   
    try:
        data = db.load()
        item = int(request.args.get('item'))
        if item >= len(data['answer_key']) or item < 0:
            abort(401, 'Invalid Item Number')
        analysis = {
            'answer_key': data['answer_key'][item],
            'correct': 0,
            'wrong': 0,
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0,
            'E': 0,
        }

        for student in data['students']:
            ans = student['eval'][item]
            if len(ans) == 1:
                analysis[ans] += 1
                if ans == analysis['answer_key']:
                    analysis['correct'] += 1
                else: analysis['wrong'] += 1
            else: analysis['wrong'] += 1
        
        return make_response(jsonify(analysis), 200)
    except Exception as e:
        abort(400)

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

    return make_response(jsonify(students), 200) 

@app.route('/student')
def getStudent():
    if request.remote_addr not in logged_in:
        return abort(403)

    id = request.args.get('id')
    students= db.get_students()
    if id >= len(students):
        abort(404, 'Student not found')

    return make_response(jsonify(students[id]), 200) 

@app.route('/student/eval_img')
def getStudentEvalImage():
    if request.remote_addr not in logged_in:
        return abort(403)

    id = request.args.get('id')
    try:
        file = f"database/output/student_{id}/eval.png"
        return send_file(file, mimetype='image/png')
    except:
        abort(400)

@app.route('/student/signature_img')
def getStudentSignatureImage():
    if request.remote_addr not in logged_in:
        return abort(403)

    id = request.args.get('id')
    try:
        file = f"database/output/student_{id}/signature.png"
        return send_file(file, mimetype='image/png')
    except:
        abort(400)
    

@app.route('/logout', methods = ['POST'])
def logout():
    if request.remote_addr not in logged_in:
        return abort(401)
    while request.remote_addr in logged_in:
        logged_in.remove(request.remote_addr)

    return make_response("Success", 200)

@app.route('/auth', methods = ['POST'])
def authenticate():
    session_id = request.args.get('session')
    if session_id == None:
        abort(400)
    if session_id != SESSION_ID:
        abort(401, 'Invalid SESSION ID')
    else:
        logged_in.add(request.remote_addr)
    return 'success'

def gen():
    global frame,cam
    while True:
        success, frame = cam.read()
        ret, buffer = cv.imencode('.jpg', cv.rotate(frame, cv.ROTATE_180))
        frame = buffer.tobytes()
        # yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        yield (b'--frame\r\n'
       b'Content-Type:image/jpeg\r\n'
       b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'
       b'\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def startServer():
    initializeCamera()
    app.run(host = '0.0.0.0', 
            port = 8000, 
            debug = False)

if __name__ == '__main__':
    startServer()    