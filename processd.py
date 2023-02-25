import cv2 as cv
import apriltag
import numpy as np
from numpy.linalg import inv
import time
import json

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

# print("Loading config")
# print(mtx, dist, coords, params, cams)

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame_time, table, cam_id):
    
    try:
        
        frame = frame_time[0]
        ti = frame_time[1]

        st = time.time()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)
                
        pose_x, pose_y, pose_z, pose_time = (), (), (), ()

        for r in results:
            if str(r.tag_id) in coords.keys():

                p3d = coords[str(r.tag_id)]
                p3d = np.array(p3d, dtype=np.float32)
                corners = np.array(r.corners, dtype=np.float32)

                p2d = cv.cornerSubPix(gray, corners, (res, res), (-1, -1), criteria)

                ret, rvecs, tvecs = cv.solvePnP(p3d, p2d, mtx, dist)

                rmtx, _ = cv.Rodrigues(rvecs)

                #cams['0']['tvec'][1] = -cams['0']['tvec'][1]

                cam = np.array(cams[str(cam_id)]['tvec'], dtype=np.float32)

                camrobot_world = np.matmul(inv(rmtx), cam.T)


                camtag_cam = [tvecs[0][0], tvecs[1][0], tvecs[2][0]]

                camtag_world = np.matmul(inv(rmtx), camtag_cam)

                print("Pose result from tag " + r.tag_id + ": " + str(camtag_world))

                for i in range(len(camtag_world)):
                    camtag_world[i] = -camtag_world[i]

                robot_world = camrobot_world + camtag_world

                pose_x += (robot_world[0],)
                pose_y += (robot_world[1],)
                pose_z += (robot_world[2],)
                pose_time += (ti,)

                
        seen = table.getBoolean("seen", False)

        # print("SHO&LD BE SEEN: " + str(seen))
        
        pxt, pyt, pzt, ptt = (), (), (), ()

        if not seen:
            pxt = table.getNumberArray("pose_x", ())
            pyt = table.getNumberArray("pose_y", ())
            pzt = table.getNumberArray("pose_z", ())
            ptt = table.getNumberArray("pose_time", ())
            
        table.putNumberArray("pose_x", pxt + pose_x)
        table.putNumberArray("pose_y", pyt + pose_y)
        table.putNumberArray("pose_z", pzt + pose_z)
        table.putNumberArray("pose_time", ptt + pose_time)
        table.putBoolean("seen", False)
        
        print("NT connection: " + str(table.isConnected()) + ", seen: " + str(seen))


        # print("Detection: " + str(time.time() - st) + ",                tags: " + str(len(results)))

    except Exception as e:
        print(e)

