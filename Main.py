import cv2 as cv
import numpy as np

from random import choice, choice, randint
from models.student import Student
from utils import checker, utils as util, database as db
_IMAGE_PATH = "images/test/test (3).jpeg"
_ANSWER_KEY = []
student_list = []

data_json = {}

def reset():
    pass

def main():
    global _ANSWER_KEY, data_json
    # _ANSWER_KEY = evaluateAnswerSheet()
    choices = ['A', 'B', 'C', 'D', 'E']
    [_ANSWER_KEY.append(choice(choices)) for _ in range(50)]
    data_json['answerKey'] = _ANSWER_KEY
    student_list.append(evaluateStudentAnswerSheet().serialize())
    data_json['students'] = student_list
    db.save_json(data_json)
    
         
def evaluateAnswerSheet() -> list:
    img = cv.imread(_IMAGE_PATH)
    
    answer_key = []
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    for items in eval:
        for item in items:
            answer = np.where(item == 1)[0]
            answer = chr(65 + answer[0]) if len(answer) == 1 else " "
            answer_key.append(answer)
    return answer_key            
    
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
    
    cv.imwrite("images/output/shaded.png", shaded_img)
    return Student(0, shaded_img, shaded_img, eval, score)
        

def clear():
    pass

if __name__ == '__main__':
    main()