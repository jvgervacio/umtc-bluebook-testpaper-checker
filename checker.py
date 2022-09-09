import cv2 as cv
import numpy as np

# IMAGE_PATH = "images/test.jpg"
IMAGE_PATH = "images/test (2).jpeg"
ANSWER_KEY_PATH = "answer_key.txt"
THRESHOLD_VAL = 100
ANSWER_KEY = []
BOX_W, BOX_H = 0, 0


def main():
    global ANSWER_KEY
    with open(ANSWER_KEY_PATH) as answer_file:
        ANSWER_KEY = answer_file.read().splitlines()  
    img = cv.imread(IMAGE_PATH)
    (img, warped_rect) = initialize(img)
    eval = evaluate(warped_rect)
    cv.imshow("output", np.hstack([resize_image(img, 200) for img in warped_rect]))
    cv.waitKey(0)
    cv.destroyAllWindows()

def initialize(img):
    img = resize_image(img, 1280)
    processed_img = preprocess(img)
    img_CONTOUR = img.copy()
    contours, _ = cv.findContours(processed_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    rect_contours = getRectContours(contours)
    warped_rect = [warpImage(img, rect) for rect in rect_contours]
    return (img, warped_rect)

    
def evaluate(rect_contours: list):
    eval = []
    # cv.imshow("output1", np.hstack([resize_image(cv.threshold(rect[30:-30], THRESHOLD_VAL, 255, cv.THRESH_BINARY_INV)[1], 200) for rect in rect_contours]))
    for rect in rect_contours:
        rect = cv.threshold(rect[30:-30], THRESHOLD_VAL, 255, cv.THRESH_BINARY_INV)[1]
        nonzero_items = [[np.count_nonzero(i) for i in item] for item in splitBoxes(rect)]
        items = []

        for item in nonzero_items:
            avg = np.mean(item)
            items.append(np.where(item > avg, 1, 0))     
        eval.append(items)
       
    # if show_answer:
    #     for i, items in enumerate(eval):
    #         for j, item in enumerate(items):
    #             index = np.where(item == 1)[0]
    #             k = j + (i * 20)
    #             if len(index) == 1 and k < len(ANSWER_KEY):
    #                 correct = False
    #                 ans = chr(65 + index[0]) 
    #                 color = (0,255,0)
    #                 if  ans == ANSWER_KEY[k]:
    #                     score+=1
    #                 else:
    #                     x = ord(ANSWER_KEY[k]) - 65
    #                     cx = (x * BOX_W) + BOX_W// 2
    #                     cy = (j * BOX_H) + BOX_H//2    
    #                     cv.circle(rect_contours[i], (cx + 95, cy+25), 15, (255, 0, 0), cv.FILLED)
    #                     color = (0,0,255)
                        
    #                 cx = (index[0] * BOX_W) + BOX_W// 2
    #                 cy = (j * BOX_H) + BOX_H//2    
    #                 cv.circle(rect_contours[i], (cx + 95, cy+25), 30, color, cv.FILLED)
    #                 print(f"{k+1:03} :",ans, ANSWER_KEY[k], correct)
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

def warpImage(img: np.ndarray, contour):
    w, h = 500, 2000
    corner_points = getReorderedCornerPoints(contour)
    pt1 = np.float32(corner_points)
    pt2 = np.float32([[0,0], [w, 0], [0,h], [w, h]])
    matrix = cv.getPerspectiveTransform(pt1, pt2)
    warped = cv.warpPerspective(img, matrix, (w, h))
    return warped

def getReorderedCornerPoints(contour):
    corner_points = getCornerPoints(contour)
    corner_points = corner_points.reshape((4,2))
    corner_points_new = np.zeros((4,1,2), np.int32)
    add = corner_points.sum(1)
    
    corner_points_new[0] = corner_points[np.argmin(add)]
    corner_points_new[3] = corner_points[np.argmax(add)]
    diff = np.diff(corner_points, axis = 1)
    corner_points_new[1] = corner_points[np.argmin(diff)]
    corner_points_new[2] = corner_points[np.argmax(diff)]
    return corner_points_new

def getCornerPoints(contour):
    peri = cv.arcLength(contour, True)
    approx = cv.approxPolyDP(contour, 0.02 * peri, True)
    return approx

def sortByXPos(contour):
    corner_points = getCornerPoints(contour)
    return corner_points[0][0][0]
    
def getRectContours(contours):
    rects = []
    for contour in contours:
        area = cv.contourArea(contour)
        if area > 10000:
            corner_points = getCornerPoints(contour)
            if len(corner_points) == 4:
                rects.append(contour)
                
    rects = sorted(rects, key = sortByXPos)
    return rects
            
def preprocess(img: np.ndarray): 
    img_GRAY = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_BLUR = cv.GaussianBlur(img_GRAY, (5,5), 1)
    img_CANNY = cv.Canny(img_BLUR, 30, 60)
    # cv.imshow("gray", img_GRAY)
    # cv.imshow("blur", img_BLUR)
    # cv.imshow("canny", img_CANNY)
    return img_CANNY

def resize_image(img: np.ndarray, new_width):
    h, w, _ = img.shape
    ratio = w/h
    WIDTH = new_width 
    HEIGHT = int(WIDTH / ratio)
    return cv.resize(img, (WIDTH, HEIGHT))
    
if __name__ == '__main__':
    main()
    