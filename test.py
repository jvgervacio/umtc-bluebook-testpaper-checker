import cv2 as cv

camera = cv.VideoCapture(-1)

while True:
    ret, frame = camera.read()
    cv.imshow('out', frame)
    key = cv.waitKey(1)
    if key == ord('q'):
        break