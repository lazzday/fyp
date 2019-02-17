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
import os

def nothing(x):
        pass

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
    calib_folder_path = '/home/liam/fyp/calib/calib_values/'
    cam_mats_left = np.load(os.path.join(calib_folder_path, 'cam_mats_left.npy'))
    cam_mats_right = np.load(os.path.join(calib_folder_path, 'cam_mats_right.npy'))
    disp_to_depth_mat = np.load(os.path.join(calib_folder_path, 'disp_to_depth_mat.npy'))
    dist_coefs_left = np.load(os.path.join(calib_folder_path, 'dist_coefs_left.npy'))
    dist_coefs_right = np.load(os.path.join(calib_folder_path, 'dist_coefs_right.npy'))
    e_mat = np.load(os.path.join(calib_folder_path, 'e_mat.npy'))
    f_mat = np.load(os.path.join(calib_folder_path, 'f_mat.npy'))
    proj_mats_left = np.load(os.path.join(calib_folder_path, 'proj_mats_left.npy'))
    proj_mats_right = np.load(os.path.join(calib_folder_path, 'proj_mats_right.npy'))
    rectification_map_left = np.load(os.path.join(calib_folder_path, 'rectification_map_left.npy'))
    rectification_map_right = np.load(os.path.join(calib_folder_path, 'rectification_map_right.npy'))
    rect_trans_left = np.load(os.path.join(calib_folder_path, 'rect_trans_left.npy'))
    rect_trans_right = np.load(os.path.join(calib_folder_path, 'rect_trans_right.npy'))
    rot_mat = np.load(os.path.join(calib_folder_path, 'rot_mat.npy'))
    trans_vec = np.load(os.path.join(calib_folder_path, 'trans_vec.npy'))
    undistortion_map_left = np.load(os.path.join(calib_folder_path, 'undistortion_map_left.npy'))
    undistortion_map_right = np.load(os.path.join(calib_folder_path, 'undistortion_map_right.npy'))
    valid_boxes_left = np.load(os.path.join(calib_folder_path, 'valid_boxes_left.npy'))
    valid_boxes_right = np.load(os.path.join(calib_folder_path, 'valid_boxes_right.npy'))
    
    left_capture = cv.VideoCapture(1)
    right_capture = cv.VideoCapture(0) 
    
    if (left_capture.isOpened() == False | left_capture.isOpened() == False):
        print("Error opening video stream")
    
    window_size = 1
    min_disp = 0
    num_disp = 160-min_disp
    
#    stereo = cv.StereoBM_create(numDisparities = 32,
#                                blockSize = 9)
    
#    cv.namedWindow('disparity')
#    cv.createTrackbar('minDisparities', 'disparity', 0, 480, nothing)
#    cv.createTrackbar('numDisparities', 'disparity', 1, 20, nothing)
#    cv.createTrackbar('blockSize', 'disparity', 1, 31, nothing)
#    cv.createTrackbar('P1', 'disparity', 0, 480, nothing)
#    cv.createTrackbar('P2', 'disparity', 0, 480, nothing)
#    cv.createTrackbar('disp12MaxDiff', 'disparity', 1, 100, nothing)
#    cv.createTrackbar('uniquenessRatio', 'disparity', 0, 20, nothing)
#    cv.createTrackbar('speckleWindowSize', 'disparity', 50, 200, nothing)
#    cv.createTrackbar('speckleRange', 'disparity', 0, 16, nothing)
    
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
            

            
            imgL = np.float32(imgL)
            imgR = np.float32(imgR)
            
            undistorted_left = np.reshape(imgL, (-1,1,2))
            undistorted_right = np.reshape(imgR, (-1,1,2))
            
            undistorted_left = cv.undistortPoints(src=undistorted_left,
                               cameraMatrix=cam_mats_left, 
                               distCoeffs=dist_coefs_left,
                               R=rect_trans_left,
                               P=proj_mats_left)
            undistorted_right = cv.undistortPoints(src=undistorted_right, 
                               cameraMatrix=cam_mats_right, 
                               distCoeffs=dist_coefs_right,
                               R=rect_trans_right,
                               P=proj_mats_right)
            
##            
#            updateSGBM()
            
            undistorted_left = np.reshape(undistorted_left, imgL.shape)
            undistorted_right = np.reshape(undistorted_right, imgR.shape)

            cv.imshow('left', undistorted_left)
            cv.imshow('right', undistorted_right)
#            concat_imgLR = cv.hconcat([undistorted_left, undistorted_right])
#            cv.imshow("left&right", concat_imgLR)
#                  
#            disparity = stereo.compute(imgL, imgR)
#            cv.imshow('disparity', disparity)
            
            if cv.waitKey(1)  & 0xFF == ord('q'):
                break
        else:
            break

    left_capture.release()
    right_capture.release()
    cv.destroyAllWindows()
