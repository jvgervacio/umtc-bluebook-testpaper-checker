import pandas as pd
import cv2 as cv
from imutils.video import VideoStream
import utils.utils as util
import utils.checker as checker
import v4l2
import os
x= 0
url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
table = pd.read_html(url)[0]
table.columns = table.columns.droplevel()
# os.system('ffmpeg -f v4l2 -i video="dev/video0" -f alsa -i hw:0 -profile:v high -pix_fmt yuvj420p -level:v 4.1 -preset ultrafast -tune zerolatency -vcodec libx264 -r 10 -b:v 512k -s 640x360 -acodec aac -strict -2 -ac 2 -ab 32k -ar 44100 -f mpegts -flush_packets 0 udp://localhost:5000?pkt_size=1316')
# cap = VideoStream(x, resolution=(640,360)).start()
cap = cv.VideoCapture(-1, cv.CAP_V4L2)
# resolutions = {}
# for index, row in table[["W", "H"]].iterrows():
#     cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     resolutions[str(width)+"x"+str(height)] = "OK"
# print(resolutions)
cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
try:
    while True:
        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        success, frame = None, None
        try:
            success, frame = cap.read()
            if not success or key == ord('q'):
                break
            
            frame, contours, warped_rect = checker.initialize(frame)
            # img = util.preprocess_img(frame)
            # cont, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
            # frame = cv.rotate(frame, cv.ROTATE_180)
            cv.drawContours(frame, contours, -1, (0, 255, 0), 2)
            # cv.imshow("signature", frame[10:150, 1220:-50])
            cv.imshow("contours" ,util.resize_image(frame, 1280))
            # cv.imshow("camera", util.resize_image(cv.hconcat(warped_rect), 1280))
        except Exception as e:
            pass
        key = cv.waitKey(1)
        
except Exception as e:
    print(e)

cap.release()
cv.destroyAllWindows()