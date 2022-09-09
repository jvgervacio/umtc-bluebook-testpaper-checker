from re import L
import checker
import cv2 as cv
import numpy as np

IMAGE_PATH = "images/test (2).jpeg"

def main():
    img = cv.imread(IMAGE_PATH)
    answer_key = getAnswerKey(img)
    print(len(answer_key))
    cv.waitKey(0)
         
def getAnswerKey(img: np.ndarray) -> list:
    answer_key = []
    img, contours = checker.initialize(img)
    eval = checker.evaluate(contours)
    for items in eval:
        for item in items:
            answer = np.where(item == 1)[0]
            answer = chr(65 + answer[0]) if len(answer) == 1 else " "
            answer_key.append(answer)
    return answer_key            
    
def getScore() -> int:
    
    pass

def clear():
    pass

if __name__ == '__main__':
    main()