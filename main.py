from asyncio import events
from curses.ascii import isalpha
import shutil
import cv2 as cv
import numpy as np
from random import choice, choice, randint
from database import database as db
from models.student import Student
from utils import checker, utils as util
import server
import RPi.GPIO as GPIO
import os

img_path = "images/test/test (8).jpg"
OUTPUT_PATH = "database/output"
n_student = 0
EVAL_PIN = 21
ANSK_PIN = 20
LED1 = 15
LED2 = 14
cam = None

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(EVAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ANSK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

def main():
    try: 
        n_student = len(db.get_students())
        GPIO.output(LED2, GPIO.HIGH)
        GPIO.output(LED1, GPIO.LOW)
        GPIO.add_event_detect(EVAL_PIN, GPIO.RISING, callback=evaluateStudentAnswerSheet, bouncetime=2000)
        GPIO.add_event_detect(ANSK_PIN, GPIO.RISING, callback=evaluateAnswerSheet, bouncetime=2000)
        server.startServer()
    except KeyboardInterrupt as e:
        print("SESSION CLOSED!")
    cleanup()

    
def cleanup():
    GPIO.remove_event_detect(EVAL_PIN)
    GPIO.remove_event_detect(ANSK_PIN)
    GPIO.cleanup()
    
def evaluateAnswerSheet(channel):
    print("[INFO] Capturing AnswerSheet...")
    GPIO.output(LED1, GPIO.LOW)
    try:
        global n_student
        n_student = 0
        answer_key = []
        frame = np.ndarray
        success, frame = server.cam.read()
        
        if not success:
            raise Exception("Failed to capture image from camera")
        
        
        frame = cv.rotate(frame, cv.ROTATE_180)   
        cv.imwrite("test.jpg", frame)
        frame, contours, warped = checker.initialize(frame)

        if len(warped) != 5:
            raise Exception("Please Align the answer sheet correctly")
        
        
        eval = checker.evaluate(warped)
        # count = 1
        for items in eval:
            for item in items:
                answer = np.where(item == 1)[0]
                # print(item)
                if len(answer) > 1:
                    raise Exception("Invalid AnswerSheet")
                
                answer = chr(65 + answer[0]) if len(answer) == 1 else " "
                # print(count, answer)
                # count+=1

                answer_key.append(answer)
        
        ans_string = ''.join(answer_key).rstrip()
        # print(ans_string)
        answer_key = [*ans_string]
        # print(answer_key)
        
        for x in answer_key:
            if not x.isalpha:
                raise Exception("Invalid AnswerSheet")
            
        session_id = db.set_answer_key(answer_key)
        print(f'[SUCCESS] Answersheet Captured (SESSION ID: {session_id})')
        if(os.path.exists(OUTPUT_PATH)):
            shutil.rmtree(OUTPUT_PATH)
        
        os.makedirs(OUTPUT_PATH)   
        cv.imwrite(f'{OUTPUT_PATH}/ANSWER_SHEET.png', util.resize_image(cv.hconcat(warped), 720))
        server.new_data = True
    except Exception as e:
        print("[ERROR] ", e)
        GPIO.output(LED1, GPIO.HIGH)
    

def evaluateStudentAnswerSheet(channel):
    print("[INFO]  Capturing Student AnswerSheet...")
    GPIO.output(LED1, GPIO.LOW)
    # try:
    global n_student
    answer_key = db.get_answer_key()
    score = 0
    try:
        success, frame = server.cam.read()
        if not success:
            raise Exception("Failed fetch frame from camera")
        frame = cv.rotate(frame, cv.ROTATE_180)  
        frame, contours, warped_img = checker.initialize(frame)
        if (len(warped_img) != 5):
            raise Exception("Please align the test paper correctly!")
        
        cv.drawContours(frame, contours, -1, (0, 255, 0), 3)
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
                        cv.circle(warped_img[i], (cx + 66, cy+5), 15, color, 5)
                    # cv.line(warped_img[i], (0, cy + 25), (30, cy + 25), color, 20) 
        
        [raw_ans.append('-') for _ in range(len(raw_ans), len(answer_key))]
        shaded_img = util.resize_image(cv.hconcat(warped_img), 720)
        
        cv.imwrite(f'{OUTPUT_PATH}/[{n_student}] EVAL.png', shaded_img)
        cv.imwrite(f'{OUTPUT_PATH}/[{n_student}] SIGNATURE.png', checker.getSignatureArea(frame))
        db.add_student(Student(n_student, raw_ans, score))
        n_student += 1
        print(F"[INFO] STUDENT_{n_student} Score:", score)
        print('[SUCCESS] Student Answer Captured')
        server.new_data = True
    except Exception as e:
        print("[ERROR] ", e) 
        GPIO.output(LED1, GPIO.HIGH)

if __name__ == '__main__':
    main()
