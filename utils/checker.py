import cv2 as cv
import numpy as np
from utils import utils as util

# IMAGE_PATH = "images/test.jpg"
THRESHOLD_VAL = 100
BOX_W, BOX_H = 0, 0

def initialize(img: np.ndarray):
    img = util.resize_image(img, 1280)
    processed_img = util.preprocess_img(img)
    img_CONTOUR = img.copy()
    contours, _ = cv.findContours(processed_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    rect_contours = getRectContours(contours)
    warped_rect = [util.warpImage(img, rect) for rect in rect_contours]
    
    # getSignatureArea(rect_contours)
    return (img, rect_contours, warped_rect)


def getSignatureArea(rect_contours: list):
    corner_pt = util.getReorderedCornerPoints(rect_contours[-1])
    # print(corner_pt)

def evaluate(rect_contours: list):
    eval = []
    for rect in rect_contours:
        rect = cv.threshold(rect[30:-30], THRESHOLD_VAL, 255, cv.THRESH_BINARY_INV)[1]
        nonzero_items = [[np.count_nonzero(i) for i in item] for item in splitBoxes(rect)]
        items = []

        for item in nonzero_items:
            avg = np.mean(item)
            items.append(np.where(item > avg, 1, 0))     
        eval.append(items)

    return eval

def splitBoxes(img: np.ndarray):
    global BOX_H, BOX_W
    boxes = []
    for box_row in np.vsplit(img, 20):
        h, w, _ = box_row.shape
        box_row = box_row[0:h , 95:w-40]
        choices = np.hsplit(box_row, 5)
        BOX_H, BOX_W, _ = choices[0].shape
        boxes.append(choices)
    return boxes


def sortByXPos(contour):
    corner_points = util.getCornerPoints(contour)
    return corner_points[0][0][0]
    
def getRectContours(contours):
    rects = []
    for contour in contours:
        area = cv.contourArea(contour)
        if area > 10000:
            corner_points = util.getCornerPoints(contour)
            if len(corner_points) == 4:
                rects.append(contour)
                
    rects = sorted(rects, key = sortByXPos)    
    return rects
            

