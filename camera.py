from threading import Thread
import subprocess
import numpy as np
import time

res = (1280, 800)

args = [
        "ffmpeg",
        "-i",
        "",
        "-f",
        "image2pipe",
        "-pix_fmt",
        "rgb24",
        "-vcodec",
        "rawvideo",
        "-",
    ]

class Stream():
    def __init__(self, src):
        
        args[2] = "/dev/video" + str(src)
        
        self.pipe = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=res[0] * res[1] * 3,
        )
        
        self.frame = None
        self.switch = False
        self.src = src
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            st = time.time()

            re = self.pipe.stdout.read(res[0] * res[1] * 3)
            if len(re) > 0:
                array = np.frombuffer(re, dtype="uint8")
                self.frame = array.reshape((res[1], res[0], 3))
                
            if self.switch:
                self.pipe.stdout.close()
                args[2] = "/dev/video" + str(self.src)
                self.switch = False
                
                self.pipe = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    bufsize=res[0] * res[1] * 3,
                )
                
            print("Cycle time: " + str(time.time() - st))
                
    def switch_cam(self, src):
        self.src = src
        self.switch = True
            
    def get(self):
        return self.frame
            