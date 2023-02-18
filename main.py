from threading import Thread
from camera import Stream
from process import detect
import time
from random import random

ids = [2, 4, 6, 8]

if __name__ == "__main__":
    # Open camera streamer widget
    stream = Stream(2)
    
    while True:
        if stream.get() is not None:
            detect(stream.get())
            if random() < 0.01:
                cam = ids[int(random() * 4)]
                #print(cam)
                stream.switch_cam(cam)
       # if stream.get() is not None:
            #detect(stream.get())

        
        
