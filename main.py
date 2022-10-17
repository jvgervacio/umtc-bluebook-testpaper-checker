from asyncio import events
import cv2 as cv
import numpy as np
from random import choice, choice, randint
from database import database as db
from models.student import Student
from utils import checker, utils as util
import server
import RPi.GPIO as GPIO


img_path = "images/test/test (8).jpg"
n_student = 0

EVAL_PIN = 21
ANSK_PIN = 20
LED1 = 15
LED2 = 14
cap = None
GPIO.setmode(GPIO.BCM)
GPIO.setup(EVAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ANSK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

def main():
    global cap
    try:
        
        n_student = len(db.get_students())
        GPIO.output(LED2, GPIO.HIGH)
        GPIO.output(LED1, GPIO.LOW)
        GPIO.add_event_detect(EVAL_PIN, GPIO.RISING, callback=evaluateStudentAnswerSheet, bouncetime=2000)
        GPIO.add_event_detect(ANSK_PIN, GPIO.RISING, callback=evaluateAnswerSheet, bouncetime=2000)
        
        server.start()
    except KeyboardInterrupt as e:
        print("SESSION CLOSED!")
    cleanup()

    
def cleanup():
    GPIO.remove_event_detect(EVAL_PIN)
    GPIO.remove_event_detect(ANSK_PIN)
    GPIO.cleanup()
def evaluateAnswerSheet(channel):
    print("Capturing AnswerSheet")
    GPIO.output(LED1, GPIO.LOW)
    try:
        global n_student
        n_student = 0
        answer_key = []
        frame = np.ndarray
        try:
            success, frame = cap.read()
        except:
            pass

        
        # if not success:
        #     raise IOError("Frame Capture Failed")

        frame, contours,warped_imgs = checker.initialize(frame)
        cv.drawContours(frame, contours, -1, (0, 255, 0), 3)
        cv.imwrite(f'database/output/test.png', frame)
        eval = checker.evaluate(warped_imgs)
        for items in eval:
            for item in items:
                answer = np.where(item == 1)[0]
                print(answer)
                if len(answer) > 1:
                    raise Exception("Invalid AnswerSheet")
                answer = chr(65 + answer[0]) if len(answer) == 1 else " "
                answer_key.append(answer)
        
        # answer_key = [choice(['A', 'B', 'C', 'D', 'E']) for _ in range(100)]
        db.set_answer_key(answer_key)
        print('answersheet captured')
    except Exception as e:
        print("Failed to capture answer key: ", e)
        GPIO.output(LED1, GPIO.HIGH)
    

def evaluateStudentAnswerSheet(channel):
    print("Capturing Student AnswerSheet")
    GPIO.output(LED1, GPIO.LOW)
    # try:
    global n_student
    answer_key = db.get_answer_key()
    score = 0
    try:
        success, frame = cap.read()
        cv.imwrite(f'database/output/test.png', frame)
        # if not success:
        #     raise Exception("Frame Capture Failed")
        
        frame, contours, warped_img = checker.initialize(frame)
        cv.drawContours(frame, contours, -1, (0, 255, 0), 3)
        cv.imwrite(f'database/output/test.png', frame)
        eval = checker.evaluate(warped_img)
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
                        cv.circle(warped_img[i], (cx + 95, cy+25), 30, (0, 255, 255), 5)
                        color = (0,0,255)

                    cx, cy = 0,0
                    if ans is None:
                        raw_ans.append('-')
                    else:
                        raw_ans.append([chr(65 + x) for x in index] if len(index) > 1 else chr(65 + index[0]))
                        
                    for x in index:
                        cx = (x * w) + w//2
                        cy = (j * h) + h//2  
                        cv.circle(warped_img[i], (cx + 95, cy+25), 30, color, 5)
                    cv.line(warped_img[i], (0, cy + 25), (30, cy + 25), color, 20) 
        
        [raw_ans.append('-') for _ in range(len(raw_ans), len(answer_key))]
        shaded_img = util.resize_image(cv.hconcat(warped_img), 720)
        # eval = np.concatenate(eval).tolist()
        cv.imwrite(f'database/output/student_{n_student}/eval.png', shaded_img)
        cv.imwrite(f'database/output/student_{n_student}/signature.png', checker.getSignatureArea(frame))
        db.add_student(Student(n_student, raw_ans, score))
        n_student += 1
        # except Exception as e:
        #     print(e)

        print('student answer captured')
    except Exception as e:
        print("Failed to capture student answer: ", e) 
        GPIO.output(LED1, GPIO.HIGH)

if __name__ == '__main__':
    main()
