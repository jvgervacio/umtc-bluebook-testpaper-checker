import cv2 as cv
import numpy as np
from utils import utils as util

# IMAGE_PATH = "images/test.jpg"
THRESHOLD_VAL = 80
BOX_W, BOX_H = 0, 0
contours = None

def initialize(img: np.ndarray):
    global contours
    
    img = util.resize_image(img, 1920)
    processed_img = util.preprocess_img(img)
    img_CONTOUR = img.copy()
    contours, _ = cv.findContours(processed_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    rect_contours = getRectContours(contours, 220000, 270000)
    warped_rects = [util.warpImage(img, contour, 400, 1280) for contour in rect_contours ]
    return (img, rect_contours, warped_rects)

def getSignatureArea(img:np.ndarray):
    rects = getRectContours(contours, 75000, 78000)
    if len(rects) == 0:
        raise Exception("Cant find Signature Area!")
    
    return util.warpImage(img, rects[0], 800, 200)

def evaluate(rect_contours: list):
    eval = []
    for i,rect in enumerate(rect_contours):
        # cv.imwrite(f"database/output/img {i}.png", rect)
        # if i == 0:
        #     cv.imwrite(f"database/output/ch.png", splitBoxes(rect[10:-10, 60:-10])[0][0])
        rect = cv.threshold(rect[10:-10, 60:-10], THRESHOLD_VAL, 255, cv.THRESH_BINARY_INV)[1]
        # cv.imwrite(f"database/output/rect {i}.png", rect)
        nonzero_items = [[np.count_nonzero(i) for i in item] for item in splitBoxes(rect)]
        
        items = []
        for i, item in enumerate(nonzero_items):
            avg = np.mean(item)
            # print(i, item)
            items.append([-1] if avg < 100 else np.where(item > avg, 1, 0))     
        eval.append(items)

    return eval

def splitBoxes(img: np.ndarray):
    global BOX_H, BOX_W
    boxes = []
    # print(img.shape)
    for box_row in np.vsplit(img, 20):
        h, w, _ = box_row.shape
        # box_row = box_row[0:h , 95:w-40]
        choices = np.hsplit(box_row, 5)
        
        BOX_H, BOX_W, _ = choices[0].shape
        boxes.append(choices)
        
    
    return boxes


def sortByXPos(contour):
    corner_points = util.getCornerPoints(contour)
    return corner_points[0][0][0]
    
def getRectContours(contours, min_area, max_area):
    rects = []
    for contour in contours:
        area =  cv.contourArea(contour)
        if area > min_area and area < max_area:
            corner_points = util.getCornerPoints(contour)
            # print(area, len(corner_points))
            if len(corner_points) == 4:
                rects.append(contour) 
                
    rects = sorted(rects, key = sortByXPos)        
    return rects
        