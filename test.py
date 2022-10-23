from cv2 import waitKey
import numpy as np
import pandas as pd
import cv2 as cv

import utils.utils as util
import utils.checker as checker

cap = cv.VideoCapture(-1, cv.CAP_V4L2)
cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
x = 0
y = 0
tresh = False
while True:
    
        success, frame = cap.read()
        frame = cv.rotate(frame, cv.ROTATE_180)
        img = frame.copy()
        frame, contours, warped, = checker.initialize(frame)
        try:
            boxes = checker.splitBoxes(warped[y][10:-10, 60:-10])
            # if tresh:
            #     boxes[x] = cv.threshold(vs[x], 100, 255, cv.THRESH_BINARY_INV)[1]
            # hs = np.hsplit(vs[x], 5)
            # nonzeros= [np.count_nonzero(h) for h in hs]
            # print(np.where(nonzeros > np.mean(nonzeros), 1, 0))
            for i,h in enumerate(boxes[x]):
                cv.namedWindow(f"{i}")
                cv.moveWindow(f"{i}", 100 + (i * 100), 300)
                cv.imshow(f"{i}", h)
        except:
            print("Index out of bounds")
            
        key = waitKey(1)
        
        if key == ord('1'):
            tresh = not tresh
        
        if key == ord('q'):
            break
        if key == ord('s'):
            x += 1
            print(x)
        if key == ord('a'):
            x -= 1
            print(x)
        if key == ord('x'):
            x = 0
            y += 1
            print(y)
        if key == ord('z'):
            x = 0
            y -= 1
            print(y)
        
cap.release()
cv.destroyAllWindows()