from threading import Thread
from camera import Stream
import time

if __name__ == "__main__":
    # Open camera streamer widget
    stream = Stream(2)
    
    while True:
        if stream.get() is not None:
            print(len(stream.get()))
        time.sleep(0.1)
        
        
