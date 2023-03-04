import cv2 as cv
import apriltag
import numpy as np
from numpy.linalg import inv
import time
import json
from mathtools import euler_from_matrix, angle

SRC = 2
TAG = 8
INFO = "D150A-2"



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

def save_json(data, file_name):
    print('Saving to file: ' + file_name)
    json_data = json.dumps(data)
    with open(file_name, 'w') as f:
        f.write(json_data)

mtx, dist, coords, params, cams = load_config()

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, params['iter'], params['eps'])
res = params['res']

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))



poses = []

print("v4l2:///dev/cams/c" + str(SRC))
camera = cv.VideoCapture("v4l2:///dev/cams/c" + str(SRC))

while True:
    ret, frame = camera.read()
    print(ret)
    
    try:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)
        
        temppose = []
        
        for r in results:
            if r.tag_id == TAG:
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

                cam = np.array(cams[str(SRC)]['tvec'], dtype=np.float32)
                cam_a = cams[str(SRC)]['euler']

                camrobot_world = np.matmul(inv(rmtx), cam.T)

                camtag_cam = [tvecs[0][0], tvecs[1][0], tvecs[2][0]]

                camtag_world = np.matmul(inv(rmtx), camtag_cam)

                for i in range(len(camtag_world)):
                    camtag_world[i] = -camtag_world[i]

                robot_world = camrobot_world + camtag_world
                
                #print(camrobot_world, camtag_world, robot_world)

                pose = (robot_world[0], robot_world[1], cam_a[2] + euler[1])
                print(pose)
                temppose.append(pose)
                
                cv.putText(frame, str(pose), (50, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv.LINE_AA)

                for i in range(4):
                    cv.circle(frame, (p2d[i][0], p2d[i][1]), 1, (0, 0, 255), -1)
                    cv.line(frame, (p2d[i][0], p2d[i][1]), (p2d[(i+1)%4][0], p2d[(i+1)%4][1]), (0, 255, 0), 1)
                
        #cv.imshow('frame', frame) 
        #k = cv.waitKey(0) & 255
        
        #if(k == ord('s')):
        if(len(temppose) > 0):
            poses += temppose
            
        if(len(poses) >= 150):
            save_json(poses, "./covf/C" + str(SRC) + "T" + str(TAG) + " " + INFO + ".json")
            quit()
        
    except Exception as e:
        print(e)
