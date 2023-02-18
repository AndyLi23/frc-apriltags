import cv2 as cv

camera = cv.VideoCapture(2)

i = 0

while True:
    ret, frame = camera.read()
    
    cv.imshow('frame', frame)
    k = cv.waitKey(0) & 255

    if(k == ord('q')):
        break
    
    if(k == ord('s')):
        cv.imwrite('./images/' + str(i) + '.jpg', frame)
        i += 1