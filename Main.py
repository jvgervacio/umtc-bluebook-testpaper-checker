import cv2 as cv
import numpy as np
from random import choice, choice, randint
from database import database as db
from models.student import Student
from utils import checker, utils as util
import os
import multiprocessing as mp

img_path = "images/test/test (3).jpeg"
n_student = 0

def main():
    # evaluateAnswerSheet()
    choices = ['A', 'B', 'C', 'D', 'E']
    capture = cv.VideoCapture(0)
    while True:
        try:
            ret, frame = capture.read()
            if ret == False:
                raise IOError
            
            img, rect_cont, _ = checker.initialize(frame)
            for c in rect_cont:
                cv.drawContours(img, c, -1, (0, 255, 0), 20)
            cv.imshow('vid', img)
            key = cv.waitKey(1)
            if key == ord('q'):
                break

            elif key == ord('a'):
                evaluateAnswerSheet(frame)
                db.set_answer_key([choice(choices) for _ in range(100)])
                print('answersheet captured')
            elif key == ord('s'):
                # evaluateStudentAnswerSheet(frame)
                db.add_student(Student(n_student, [choice(choices) for _ in range(100)], 0))
                print('student answersheet captured')
            
        except KeyboardInterrupt:
            break
    capture.release()
    cv.destroyAllWindows()
    
    # evaluateStudentAnswerSheet()
    # _STUDENTS.append()
    # _DATA['students'] = _STUDENTS
    # db.save_json(_DATA)

def evaluateAnswerSheet(frame: np.ndarray):
    global answer_keys
    answer_key = []
    img, _, contours = checker.initialize(frame)
    eval = checker.evaluate(contours)
    for items in eval:
        for item in items:
            answer = np.where(item == 1)[0]
            if len(answer) > 1: return
            answer = chr(65 + answer[0]) if len(answer) == 1 else " "
            answer_key.append(answer)
    db.set_answer_key(answer_key)

def evaluateStudentAnswerSheet(frame: np.ndarray):
    global n_student
    answer_key = db.get_answer_key()
    print(len(answer_key))
    score = 0
    _ , _ , contours = checker.initialize(frame)
    eval = checker.evaluate(contours)
    w, h = checker.BOX_W, checker.BOX_H
    raw_ans = []
    for i, items in enumerate(eval):
        for j, item in enumerate(items):
            index = np.where(item == 1)[0]
            k = j + (i * 20)
            if  k < len(answer_key):
                ans = chr(65 + index[0])           
                color = (0,255,0)
                if  len(index) == 1 and ans == answer_key[k]:
                    score +=1
                else:
                    x = ord(answer_key[k]) - 65
                    cx = (x * w) + w//2
                    cy = (j * h) + h//2
                    cv.circle(contours[i], (cx + 95, cy+25), 30, (0, 255, 255), 5)
                    color = (0,0,255)

                cx, cy = 0,0
                raw_ans.append([chr(65 + x) for x in index] if len(index) > 1 else chr(65 + index[0]))
                for x in index:
                    cx = (x * w) + w//2
                    cy = (j * h) + h//2  
                    cv.circle(contours[i], (cx + 95, cy+25), 30, color, 5)
                cv.line(contours[i], (0, cy + 25), (30, cy + 25), color, 20) 


    [raw_ans.append('-') for _ in range(len(raw_ans), len(answer_key))]
    shaded_img = util.resize_image(cv.hconcat(contours), 720)
    eval = np.concatenate(eval).tolist()
    eval_imgpath = f'database/output/student_{n_student}_EVAL.png'
    cv.imwrite(eval_imgpath, shaded_img)
    db.add_student(Student(n_student, raw_ans, score))
    n_student += 1
        
if __name__ == '__main__':
    # os.system("start /wait cmd /c pythonw server/server.py")
    main()
