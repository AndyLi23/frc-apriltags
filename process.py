import cv2 as cv
import apriltag
import numpy as np
import time
import json

def load_config():
    d = json.load(open('config.json'))
    mtx, dist = load_cam_config(d['calibration'])
    coords = d['coords']
    params = d['params']

    return mtx, dist, coords, params

def load_cam_config(file):
    d = json.load(open(file))

    mtx = np.array(d['camera_matrix'])
    dist = np.array(d['dist_coeffs'])

    return mtx, dist

mtx, dist, coords, params = load_config()

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, params['iter'], params['eps'])
res = params['res']

print(mtx, dist, coords, params)

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame):

    st = time.time()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    results = detector.detect(gray)
    
    for r in results:
        if str(r.tag_id) in coords.keys():

            p3d = coords[str(r.tag_id)]
            p3d = np.array(p3d, dtype=np.float32)
            corners = np.array(r.corners, dtype=np.float32)

            p2d = cv.cornerSubPix(gray, corners, (res, res), (-1, -1), criteria)

            ret, rvecs, tvecs = cv.solvePnP(p3d, p2d, mtx, dist)

            #for i in range(4):
            #    cv.circle(frame, (p2d[i][0], p2d[i][1]), 1, (0, 0, 255), -1)
            #    cv.line(frame, (p2d[i][0], p2d[i][1]), (p2d[(i+1)%4][0], p2d[(i+1)%4][1]), (0, 255, 0), 1)
            #
            #tests = []
            #for i in range(4):
            #    test, jac = cv.projectPoints(np.array(coords[str(r.tag_id)][i], dtype=np.float32), rvecs, tvecs, mtx, dist)
            #    tests.append(test)
            #
            #for i in range(4):
            #    #print(tests[(i+1)%4][0][0])
            #    cv.line(frame, tuple(tests[i][0][0]), tuple(tests[(i+1)%4][0][0]), (0, 0, 255), 1)
            #
            #cv.putText(frame, str(tvecs), (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv.LINE_AA)



    print("Detection: " + str(time.time() - st) + ",                tags: " + str(len(results)))

    #print(len(results))
 
    #cv.imshow('frame', frame) 
    #k = cv.waitKey(0) & 255

