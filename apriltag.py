import cv2 as cv
import apriltag
import numpy as np

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame):
    results = detector.detect(gray)
    
    print(results)

