from PIL import Image
import cv2 as cv
import base64
import numpy as np

def serialize_img(img: np.ndarray) -> bytes:
    print(type(img))
    if type(img) == np.ndarray:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        return base64.b64encode(img.tobytes()).decode('utf-8')
    return None

def preprocess_img(img: np.ndarray): 
    img_GRAY = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img_BLUR = cv.GaussianBlur(img_GRAY, (5,5), 3)
    # img_LAP = cv.Laplacian(img_BLUR, cv.CV_64FC4, ksize=3)
    ret, thresh = cv.threshold(img_BLUR, 100, 255, cv.THRESH_BINARY_INV)
    img_CANNY = cv.Canny(thresh, 30, 100)
    # cv.imshow("thresh", resize_image(thresh,  1280))
    # cv.imshow("canny", resize_image(img_CANNY,  1280))
    return img_CANNY

def resize_image(img: np.ndarray, new_width):
    h = 0
    w = 0
    try:
        h, w, _ = img.shape
    except ValueError:
        h, w = img.shape
    ratio = w/h
    WIDTH = new_width 
    HEIGHT = int(WIDTH / ratio)
    return cv.resize(img, (WIDTH, HEIGHT))

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