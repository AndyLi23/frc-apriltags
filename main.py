from camera import Stream
from processd import detect
from networktables import NetworkTables
import time

TEAM = 1351
PORT = 1735
IDS = [0, 1, 2, 3]
TABLE_NAME = "dashboard"

print("Connecting to NetworkTables")

NetworkTables.startClientTeam(TEAM)
NetworkTables.startDSClient(PORT)

table = NetworkTables.getTable(TABLE_NAME)


print("Loading stream")

if __name__ == "__main__":
    # Open camera streamer widget
    stream = Stream(2)
    
    print("Starting main loop")
    while True:
        # print(NetworkTables.isConnected())
        if stream.available():
            stream.read()
            g = stream.get()
            if g[0] is not None:
                detect(g, table, stream.src)

        
        
