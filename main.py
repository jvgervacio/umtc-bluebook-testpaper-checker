from asyncio import events
import cv2 as cv
import numpy as np
from random import choice, choice, randint
from database import database as db
from models.student import Student
from utils import checker, utils as util
import server
import time


img_path = "images/test/test (8).jpg"
n_student = 0


EVAL_PIN = 21
ANSK_PIN = 20

# ANSWERSHEET_CAPTURE_BTN = Button(ANSK_PIN)

def main():
    
    # try:
    #     # ANSWERSHEET_CAPTURE_BTN.when_released = evaluateAnswerSheet
    #     showCamera()
    #     # server.start(True)
    # except:
    #     pass
    evaluateAnswerSheet()
    evaluateStudentAnswerSheet()


def showCamera():
    cam = cv.VideoCapture(-1)
    while True:
        try:
            
            ret, frame = cam.read()
            # print(frame)
            key = cv.waitKey(1)
            if ret is None:
                raise IOError
            
            if key == ord('q'):
                raise KeyboardInterrupt

            if key == ord('a'):
                evaluateAnswerSheet()

            if key == ord('s'):
                evaluateStudentAnswerSheet()

            # processed_img = util.preprocess_img()
            # contours, _ = cv.findContours(processed_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            frame, contours, _ = checker.initialize(frame)
            # for contour in contours:
            cv.drawContours(frame, contours, -1, (0, 255, 0), 3)
                

            cv.imshow('output', frame)
            
        except:
            break

def evaluateAnswerSheet():
    global n_student
    n_student = 0
    answer_key = []
    try:
        ret, frame = cv.VideoCapture(-1).read()
        if ret == False:
            raise IOError
        contours = checker.initialize(frame)[2]
        eval = checker.evaluate(contours)
        for items in eval:
            for item in items:
                answer = np.where(item == 1)[0]
                if len(answer) > 1: return
                answer = chr(65 + answer[0]) if len(answer) == 1 else " "
                answer_key.append(answer)
    except:
        answer_key = [choice(['A', 'B', 'C', 'D', 'E']) for _ in range(100)]
    
    answer_key = [choice(['A', 'B', 'C', 'D', 'E']) for _ in range(100)]
    db.set_answer_key(answer_key)
    print('answersheet captured')

def evaluateStudentAnswerSheet():
    global n_student
    answer_key = db.get_answer_key()
    score = 0
    # try:
    # ret, frame = cv.VideoCapture(0).read()
    
    # if ret == False:
    #     raise IOError

    frame = cv.imread(img_path)
    contours = checker.initialize(frame)[2]
    eval = checker.evaluate(contours)
    w, h = checker.BOX_W, checker.BOX_H
    raw_ans = []
    for i, items in enumerate(eval):
        for j, item in enumerate(items):
            index = np.where(item == 1)[0]
            
            k = j + (i * 20)
            if  k < len(answer_key):
                
                ans = None if len(index) == 0 else chr(65 + index[0])        
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
                if ans is None:
                    raw_ans.append('-')
                else:
                    raw_ans.append([chr(65 + x) for x in index] if len(index) > 1 else chr(65 + index[0]))
                    
                for x in index:
                    cx = (x * w) + w//2
                    cy = (j * h) + h//2  
                    cv.circle(contours[i], (cx + 95, cy+25), 30, color, 5)
                cv.line(contours[i], (0, cy + 25), (30, cy + 25), color, 20) 

    [raw_ans.append('-') for _ in range(len(raw_ans), len(answer_key))]
    shaded_img = util.resize_image(cv.hconcat(contours), 720)
    # eval = np.concatenate(eval).tolist()
    cv.imwrite(f'database/output/student_{n_student}_EVAL.png', shaded_img)
    db.add_student(Student(n_student, raw_ans, score))
    n_student += 1
    # except Exception as e:
    #     print(e)

    print('student answer captured') 

if __name__ == '__main__':
    main()
