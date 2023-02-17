import subprocess
import numpy as np
import time

res = (1280, 800)

def read_frames(path1, path2, res):
    args = [
        "ffmpeg",
        "-i",
        path1,
        "-f",
        "image2pipe",
        "-pix_fmt",
        "rgb24",
        "-vcodec",
        "rawvideo",
        "-",
    ]

    pipe = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=res[0] * res[1] * 3,
    )

    #while pipe.poll() is None:
    frame = pipe.stdout.read(res[0] * res[1] * 3)

        #pipe.stdout.close()
    if len(frame) > 0:
        array = np.frombuffer(frame, dtype="uint8")
        print(array.reshape((res[1], res[0], 3)))

    pipe.stdout.close()

    args[2] = path2

    pipe = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=res[0] * res[1] * 3,
    )

    #while pipe.poll() is None:
    frame = pipe.stdout.read(res[0] * res[1] * 3)

        #pipe.stdout.close()
    if len(frame) > 0:
        array = np.frombuffer(frame, dtype="uint8")
        print(array.reshape((res[1], res[0], 3)))
        print("Second One")


read_frames("/dev/video2", "/dev/video4", res)