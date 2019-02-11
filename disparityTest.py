'''
***************************************
Liam Day
Bachelor of Engineering (Honours) in Software & Electronic Engineering
GMIT
2019
Final Year Project: 
Projectile Detection and Interaction
***************************************
'''
# Python 2/3 compatibility
from __future__ import print_function

#import imutils
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def nothing(x):
        pass

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')

def updateSGBM():
    # Blocksize must be an odd number, so round it down if bar is even
    _block_size = cv.getTrackbarPos('blockSize', 'disparity');
    if(_block_size % 2 == 0 & _block_size > 0):
        _block_size -= 1
    stereo.setMinDisparity(cv.getTrackbarPos('minDisparities','disparity'))
    stereo.setNumDisparities(cv.getTrackbarPos('numDisparities','disparity')*16)
    stereo.setBlockSize(_block_size)
    stereo.setP1(cv.getTrackbarPos('P1','disparity'))
    stereo.setP2(cv.getTrackbarPos('P2','disparity'))
    stereo.setDisp12MaxDiff(cv.getTrackbarPos('disp12MaxDiff','disparity'))
    stereo.setUniquenessRatio(cv.getTrackbarPos('uniquenessRatio','disparity'))
    stereo.setSpeckleWindowSize(cv.getTrackbarPos('speckleWindowSize','disparity'))
    stereo.setSpeckleRange(cv.getTrackbarPos('speckleRange','disparity'))

if __name__ == '__main__':
    print('loading images...')
    
#    cams_test = 10
#    for i in range(0, cams_test):
#        cap = cv.VideoCapture(i)
#        test, frame = cap.read()
#        print("i : "+ str(i) + "/// result: " + str(test))
#        cap.release()
    
    left_capture = cv.VideoCapture(1)
    right_capture = cv.VideoCapture(0) 
    
    if (left_capture.isOpened() == False | left_capture.isOpened() == False):
        print("Error opening video stream")
    
    window_size = 1
    min_disp = 0
    num_disp = 160-min_disp
    
    
#    stereo = cv.StereoBM_create(numDisparities = 32,
#                                blockSize = 9)
    
    cv.namedWindow('disparity')
    cv.createTrackbar('minDisparities', 'disparity', 0, 480, nothing)
    cv.createTrackbar('numDisparities', 'disparity', 1, 20, nothing)
    cv.createTrackbar('blockSize', 'disparity', 1, 31, nothing)
    cv.createTrackbar('P1', 'disparity', 0, 480, nothing)
    cv.createTrackbar('P2', 'disparity', 0, 480, nothing)
    cv.createTrackbar('disp12MaxDiff', 'disparity', 1, 100, nothing)
    cv.createTrackbar('uniquenessRatio', 'disparity', 0, 20, nothing)
    cv.createTrackbar('speckleWindowSize', 'disparity', 50, 200, nothing)
    cv.createTrackbar('speckleRange', 'disparity', 0, 16, nothing)
    
    stereo = cv.StereoSGBM_create(minDisparity = min_disp,
                numDisparities = num_disp,
                blockSize = 16,
                P1 = 8*3*window_size**2,
                P2 = 32*3*window_size**2,
                disp12MaxDiff = 1,
                uniquenessRatio = 100,
                speckleWindowSize = 10,
                speckleRange = 16)
    
    while (left_capture.isOpened() & right_capture.isOpened()):
        
        ret1, imgL = left_capture.read()
        ret2, imgR = right_capture.read()
            
        if(ret1 & ret2):
            
            updateSGBM()

            cv.imshow('left', imgL)
            cv.imshow('right', imgR)
                  
            disparity = stereo.compute(imgL, imgR)
            cv.imshow('disparity', disparity)
            
            if cv.waitKey(1)  & 0xFF == ord('q'):
                break
        else:
            break

    left_capture.release()
    right_capture.release()
    cv.destroyAllWindows()
