import cv2 as cv

while True:
    for i in range(4):
        print(i)
        camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(i))
        
        ret, frame = camera.read()
        
        cv.imshow('frame', frame) 
        k = cv.waitKey(0) & 255
        
        camera.release()