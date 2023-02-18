from threading import Thread
from camera import Stream
from apriltag import detect
import time

if __name__ == "__main__":
    # Open camera streamer widget
    stream = Stream(4)
    
    while True:
        if stream.get() is not None:
            detect(stream.get())

        
        
