from threading import Thread
import cv2 as cv
import time

class Stream():
    def __init__(self, src):
        
        print("Opening v4l2:///dev/cams/c" + str(src))
        
        self.camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(src))

        self.frame = (None, time.time_ns())
        self.switch = False
        self.switching = False;
        self.src = src
        self.new = False
        
        print("\n————————\n")
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            try:
                ti = time.time_ns()
                st = time.time()
                
                if self.switch:
                    if not self.switching:
                        self.switching = True
                        print("\n————————\n")
                        print("Switching to camera v4l2:///dev/cams/c" + str(self.src))
                        self.camera.release()
                        self.camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(self.src))
                        self.switch = False
                        print("Switched cameras in " + str(time.time() - st) + "s")
                        print("\n————————\n")
                        self.switching = False
                else:
                    ret, frame = self.camera.read()

                    if ret:
                        self.frame = (frame, ti)
                        self.new = True
                        print("Cycle time: " + str(time.time() - st) + " , id: " + str(self.src))
                    else:
                        print("\n————————\n")
                        print("Frame failed, resetting camera")
                        self.camera.release()
                        self.camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(self.src))
                        print("Camera switched successfully")
                        print("\n————————\n")
            except:
                print("Frame failed with camera " + self.camera)
                
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
            
