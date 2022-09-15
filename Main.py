import cv2 as cv
import numpy as np
from random import choice, choice, randint
from models.student import Student
from utils import checker, utils as util, database as db
import os
import multiprocessing as mp

img_path = "images/test/test (3).jpeg"
n_student = 0
def main():
    # evaluateAnswerSheet()
    choices = ['A', 'B', 'C', 'D', 'E']
    db.set_answer_key([choice(choices) for _ in range(100)])
    evaluateStudentAnswerSheet()
    # _STUDENTS.append()
    # _DATA['students'] = _STUDENTS
    # db.save_json(_DATA)

def evaluateAnswerSheet():
    global answer_key, n_student
    answer_key = []
    n_student = 0
    img = cv.imread(img_path)
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    for items in eval:
        for item in items:
            answer = np.where(item == 1)[0]
            if len(answer) > 1: return
            answer = chr(65 + answer[0]) if len(answer) == 1 else " "
            answer_key.append(answer)
    
    db.set_answer_key(answer_key)

def evaluateStudentAnswerSheet():
    global n_student
    answer_key = db.get_answer_key()
    print(len(answer_key))
    score = 0
    img = cv.imread(img_path)
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    w, h = checker.BOX_W, checker.BOX_H

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
                for x in index:
                    cx = (x * w) + w//2
                    cy = (j * h) + h//2  
                    cv.circle(contours[i], (cx + 95, cy+25), 30, color, 5)
                cv.line(contours[i], (0, cy + 25), (30, cy + 25), color, 20) 

    shaded_img = util.resize_image(cv.hconcat(contours), 720)
    eval = np.concatenate(eval).tolist()
    eval_imgpath = f'images/output/student_{n_student}.png'
    cv.imwrite(eval_imgpath, shaded_img)
    db.add_student(Student(eval_imgpath, eval_imgpath, eval, score))
    n_student += 1
        
if __name__ == '__main__':
    os.system("start /wait cmd /c pythonw server/server.py")
    main()
