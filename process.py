import cv2 as cv
import apriltag
import numpy as np

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    results = detector.detect(gray)
    
    print(results)

