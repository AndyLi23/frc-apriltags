import cv2 as cv
import apriltag
import numpy as np
import time

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame):

    st = time.time()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    results = detector.detect(gray)
    
    for r in results: 
        (ptA, ptB, ptC, ptD) = r.corners 
        ptB = (int(ptB[0]), int(ptB[1])) 
        ptC = (int(ptC[0]), int(ptC[1])) 
        ptD = (int(ptD[0]), int(ptD[1])) 
        ptA = (int(ptA[0]), int(ptA[1])) 
 
        cv.line(frame, ptA, ptB, (0, 255, 0), 1) 
        cv.line(frame, ptB, ptC, (0, 255, 0), 1) 
        cv.line(frame, ptC, ptD, (0, 255, 0), 1) 
        cv.line(frame, ptD, ptA, (0, 255, 0), 1) 
 
        (cX, cY) = (int(r.center[0]), int(r.center[1])) 
        cv.circle(frame, (cX, cY), 3, (0, 0, 255), -1)

    print("Detection: " + str(time.time() - st) + ",                tags: " + str(len(results)))

    #print(len(results))
 
    cv.imshow('frame', frame) 
    k = cv.waitKey(0) & 255

