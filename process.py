import cv2 as cv
import process
import numpy as np

detector = process.Detector(process.DetectorOptions(families='tag16h5'))

def detect(frame):
    results = detector.detect(frame)
    
    print(results)

