import cv2 as cv
import time

camera = cv.VideoCapture("v4l2:///dev/cams/c0")

i = 24

while True:
    ret, frame = camera.read()

    cv.imshow('frame', frame)
    k = cv.waitKey(0)

    if(k == ord('q')):
        break
    
    if(k == ord('s')):
        cv.imwrite('./images_c0/' + str(i) + '.jpg', frame)
        i += 1
