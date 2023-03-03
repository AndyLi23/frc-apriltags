import cv2 as cv
import apriltag
import numpy as np
from numpy.linalg import inv
import time
import json
from mathtools import euler_from_matrix

def load_config():
    d = json.load(open('config.json'))
    mtx, dist = load_cam_config(d['calibration'])
    coords = d['coords']
    cams = d['cams']
    params = d['params']

    return mtx, dist, coords, params, cams

def load_cam_config(file):
    d = json.load(open(file))

    mtx = np.array(d['camera_matrix'])
    dist = np.array(d['dist_coeffs'])

    return mtx, dist

mtx, dist, coords, params, cams = load_config()

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, params['iter'], params['eps'])
res = params['res']

print("Loading config")
print(mtx, dist, coords, params, cams)
print("\n————————\n")

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame_time, table, cam_id):
    try:
        frame = frame_time[0]
        ti = frame_time[1]

        st = time.time()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)
        
        n = 0
        
        for r in results:
            if str(r.tag_id) in coords.keys():

                p3d = coords[str(r.tag_id)]
                p3d = np.array(p3d, dtype=np.float32)
                corners = np.array(r.corners, dtype=np.float32)

                p2d = cv.cornerSubPix(gray, corners, (res, res), (-1, -1), criteria)

                ret, rvecs, tvecs = cv.solvePnP(p3d, p2d, mtx, dist)

                rmtx, _ = cv.Rodrigues(rvecs)
                
                rotation_matrix = np.array([[0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 1]],
                            dtype=float)
                rotation_matrix[:3, :3] = rmtx

                euler = euler_from_matrix(rotation_matrix)

                cam = np.array(cams[str(cam_id)]['tvec'], dtype=np.float32)
                cam_a = cams[str(cam_id)]['euler']

                camrobot_world = np.matmul(inv(rmtx), cam.T)

                camtag_cam = [tvecs[0][0], tvecs[1][0], tvecs[2][0]]

                camtag_world = np.matmul(inv(rmtx), camtag_cam)

                for i in range(len(camtag_world)):
                    camtag_world[i] = -camtag_world[i]

                robot_world = camrobot_world + camtag_world

                pose = (robot_world[0], robot_world[1], robot_world[2], cam_a[2] + euler[1], ti)
                print(pose)
                
                table.putNumberArray("pose", pose)

        print("Detection: " + str(time.time() - st) + ",                tags: " + str(len(results)))

    except Exception as e:
        print(e)

