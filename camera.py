from threading import Thread
import cv2 as cv
import numpy as np
import time

class Stream():
    def __init__(self, src):
        
        self.camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(src))

        self.frame = (None, time.time())
        self.switch = False
        self.src = src
        self.new = False
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            st = time.time()

            ret, frame = self.camera.read()

            if ret:
                self.frame = (frame, st)
                self.new = True

            while self.switch:
                self.switch = False
                self.camera.release()
                self.camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(self.src))

            # if ret: print("Cycle time: " + str(time.time() - st) + " , id: " + str(self.src))
                
    def switch_cam(self, src):
        if src != self.src:
            self.src = src
            self.switch = True
            
    def get(self):
        return self.frame
    
    def available(self):
        return self.new
    
    def read(self):
        self.new = False
            
