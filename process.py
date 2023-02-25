import cv2 as cv
import apriltag
import numpy as np
from numpy.linalg import inv
import time
import json
from mathtools import euler_from_matrix, angle

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

detector = apriltag.Detector(apriltag.DetectorOptions(families='tag16h5'))

def detect(frame_time, table, cam_id):
    
    try:
        
        frame = frame_time[0]
        ti = frame_time[1]

        st = time.time()

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)
        
        n = 0
        
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

                cv.putText(frame, str(camrobot_world), (50, 60 + 40 * n), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)
                n+=1

                camtag_cam = [tvecs[0][0], tvecs[1][0], tvecs[2][0]]

                camtag_world = np.matmul(inv(rmtx), camtag_cam)

                print(camtag_world)

                for i in range(len(camtag_world)):
                    camtag_world[i] = -camtag_world[i]

                cv.putText(frame, str(camtag_world), (50, 60 + 40 * n), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)
                n+=1

                robot_world = camrobot_world + camtag_world
                
                #print(camrobot_world, camtag_world, robot_world)
                cv.putText(frame, str(robot_world), (50, 60 + 40 * n), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv.LINE_AA)

                n+=1

                pose_x += (robot_world[0],)
                pose_y += (robot_world[1],)
                pose_z += (robot_world[2],)
                pose_time += (ti,)

                rotation_matrix = np.array([[0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 0],
                        [0, 0, 0, 1]],
                            dtype=float)
                rotation_matrix[:3, :3] = rmtx

                euler = euler_from_matrix(rotation_matrix)


                for i in range(4):
                    cv.circle(frame, (p2d[i][0], p2d[i][1]), 1, (0, 0, 255), -1)
                    cv.line(frame, (p2d[i][0], p2d[i][1]), (p2d[(i+1)%4][0], p2d[(i+1)%4][1]), (0, 255, 0), 1)
                
                tests = []

                tests.append(cv.projectPoints(np.array([0, 0, 6], dtype=np.float32), rvecs, tvecs, mtx, dist)[0])

                for i in range(4):
                    test, jac = cv.projectPoints(np.array(coords[str(r.tag_id)][i], dtype=np.float32), rvecs, tvecs, mtx, dist)
                    tests.append(test)
                    cv.putText(frame, str(coords[str(r.tag_id)][i]), tuple(test[0][0]), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv.LINE_AA)

                tests[0], tests[4] = tests[4], tests[0]
                
                for i in range(5):
                    #print(tests[(i+1)%4][0][0])
                    cv.line(frame, tuple(tests[i][0][0]), tuple(tests[(i+1)%4][0][0]), (0, 0, 255), 1)
                
                info = "ID:{}  |  X:{:.2f} Y:{:.2f} Z:{:.2f}  |  a:{:.2f} b:{:.2f} g:{:.2f}".format(r.tag_id, tvecs[0][0], tvecs[1][0], tvecs[2][0], angle(euler[0]), angle(euler[1]), angle(euler[2]))

                cv.putText(frame, info, (50, 60 + 40 * n), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)
                #cv.putText(frame, "abg: " + str(euler), (50, 80), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv.LINE_AA)

                n += 1
                
        seen = table.getBoolean("seen", False)

        print("SHO&LD BE SEEN: " + str(seen))
        
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


        print("Detection: " + str(time.time() - st) + ",                tags: " + str(len(results)))

        #print(len(results))
    
        cv.imshow('frame', frame) 
        k = cv.waitKey(0) & 255
    except Exception as e:
        print(e)

