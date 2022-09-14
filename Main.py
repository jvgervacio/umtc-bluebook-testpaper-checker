import cv2 as cv
import numpy as np
import random
from random import choice, choice, randint
from models.student import Student
from utils import checker, utils as util, database as db

_IMAGE_PATH = "images/test/test (3).jpeg"

def main():
    global _ANSWER_KEY, _DATA
    # _ANSWER_KEY = evaluateAnswerSheet()
    # choices = ['A', 'B', 'C', 'D', 'E']
    # [_ANSWER_KEY.append(choice(choices)) for _ in range(50)]
    # _DATA['answerKey'] = _ANSWER_KEY
    # _STUDENTS.append(evaluateStudentAnswerSheet().serialize())
    # _DATA['students'] = _STUDENTS
    # db.save_json(_DATA)

def evaluateAnswerSheet() -> list:
    global _ANSWER_KEY
    _ANSWER_KEY = []

    img = cv.imread(_IMAGE_PATH)
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    for items in eval:
        for item in items:
            answer = np.where(item == 1)[0]
            answer = chr(65 + answer[0]) if len(answer) == 1 else " "
            _ANSWER_KEY.append(answer)
    
    random_id = str(random.randint(0, 999999))        
    
def evaluateStudentAnswerSheet() -> Student:
    score = 0
    img = cv.imread(_IMAGE_PATH)
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    w, h = checker.BOX_W, checker.BOX_H
    for i, items in enumerate(eval):
        for j, item in enumerate(items):
            index = np.where(item == 1)[0]
            k = j + (i * 20)
            if  k < len(_ANSWER_KEY):
                ans = chr(65 + index[0]) 
                color = (0,255,0)
                if  len(index) == 1 and ans == _ANSWER_KEY[k]:
                    score +=1
                else:
                    x = ord(_ANSWER_KEY[k]) - 65
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
    # cv.imwrite("images/output/shaded.png", shaded_img)
    db.add_student(Student(np.ndarray((50,50,3)), shaded_img, eval, score)) 
        

def clear():
    pass

if __name__ == '__main__':
    main()