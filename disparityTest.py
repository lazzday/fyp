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

import imutils
import numpy as np
import cv2 as cv
import os


def nothing(x):
        pass

def updateSGBM():
    # Blocksize must be an odd number, so round it down if bar is even
    _block_size = cv.getTrackbarPos('blockSize', 'disparity');
    if(_block_size % 2 == 0 & _block_size > 0):
        _block_size -= 1
    stereo.setMinDisparity(cv.getTrackbarPos('minDisparities','disparity'))
    # NumDisparities must be divisible by 16
    stereo.setNumDisparities(cv.getTrackbarPos('numDisparities','disparity')*16)
    stereo.setBlockSize(_block_size)
    stereo.setP1(cv.getTrackbarPos('P1','disparity'))
    stereo.setP2(cv.getTrackbarPos('P2','disparity'))
    stereo.setDisp12MaxDiff(cv.getTrackbarPos('disp12MaxDiff','disparity'))
    stereo.setPreFilterCap(cv.getTrackbarPos('preFilterCap', 'disparity'))
    stereo.setUniquenessRatio(cv.getTrackbarPos('uniquenessRatio','disparity'))
    stereo.setSpeckleWindowSize(cv.getTrackbarPos('speckleWindowSize','disparity'))
    stereo.setSpeckleRange(cv.getTrackbarPos('speckleRange','disparity')) 
    
    

if __name__ == '__main__':
    
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
#                                blockSize = 5)
#    
    cv.namedWindow('disparity')
    cv.createTrackbar('minDisparities', 'disparity', -100, 480, nothing)
    cv.createTrackbar('numDisparities', 'disparity', 1, 40, nothing)
    cv.createTrackbar('blockSize', 'disparity', 5, 31, nothing)
    cv.createTrackbar('P1', 'disparity', 0, 480, nothing)
    cv.createTrackbar('P2', 'disparity', 0, 480, nothing)
    cv.createTrackbar('disp12MaxDiff', 'disparity', 1, 100, nothing)
    cv.createTrackbar('preFilterCap', 'disparity', 0, 100, nothing)
    cv.createTrackbar('uniquenessRatio', 'disparity', 0, 20, nothing)
    cv.createTrackbar('speckleWindowSize', 'disparity', 50, 200, nothing)
    cv.createTrackbar('speckleRange', 'disparity', 5, 16, nothing)
    
    stereo = cv.StereoSGBM_create(minDisparity = min_disp,
                numDisparities = num_disp,
                blockSize = 16,
                P1 = 8*3*window_size**2,
                P2 = 32*3*window_size**2,
                preFilterCap = 0,
                disp12MaxDiff = 1,
                uniquenessRatio = 100,
                speckleWindowSize = 10,
                speckleRange = 16)
    
    ret1, imgL = left_capture.read()
    ret2, imgR = right_capture.read()
    
    while (left_capture.isOpened() & right_capture.isOpened()):
        
        
            
        if(ret1 & ret2):
          
            updateSGBM()

    
            undistorted_left = cv.remap(src=imgL,
                                        map1=undistortion_map_left,
                                        map2=rectification_map_left,
                                        interpolation=cv.INTER_LINEAR)
            
            undistorted_right = cv.remap(src=imgR,
                                        map1=undistortion_map_right,
                                        map2=rectification_map_right,
                                        interpolation=cv.INTER_LINEAR)
            
            undistorted_left = cv.cvtColor(undistorted_left, cv.COLOR_BGR2GRAY)
            undistorted_right = cv.cvtColor(undistorted_right, cv.COLOR_BGR2GRAY)
            
            undistorted_left = imutils.rotate(undistorted_left, 180)
            undistorted_right = imutils.rotate(undistorted_right, 180)

#            concat_imgLR = cv.hconcat([undistorted_left, undistorted_right])
#        
#            cv.imshow("left&right", concat_imgLR)
            cv.imshow('left', undistorted_left)
            cv.imshow('right', undistorted_right)      
            disparity = stereo.compute(undistorted_left, undistorted_right)
            
            cv.imshow('disparity', disparity)
            
            if cv.waitKey(1)  & 0xFF == ord('q'):
                break
        else:
            break

    left_capture.release()
    right_capture.release()
    cv.destroyAllWindows()























































