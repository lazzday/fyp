#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Simple script to test the viewing position of the camera for setup purposes
Red lines show the 3d-point recording thresholds 
'''


import freenect
import cv2 as cv
import numpy as np

#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv.cvtColor(array,cv.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth(format=freenect.DEPTH_REGISTERED)
#    
    return array



if __name__ == "__main__":
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    while True:
        frame = get_video()
#        depth = get_depth()
        
        # Blur frame and convert to HSV color space
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, greenLower, greenUpper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        
        cv.line(frame, (40, 0), (40, 480), color=(0,0,255), thickness=2)
        cv.line(frame, (600, 0), (600, 480), color=(0,0,255), thickness=2)
        
        cv.line(frame, (0, 40), (640, 40), color=(0,0,255), thickness=2)
        cv.line(frame, (0, 440), (640, 440), color=(0,0,255), thickness=2)
        
#        cv.line(depth, (40, 0), (40, 480), color=(0,0,255), thickness=2)
#        cv.line(depth, (600, 0), (600, 480), color=(0,0,255), thickness=2)
        
        cv.imshow('RGB image',frame)
        cv.imshow('Mask', mask)
        #display depth image
#        depthImage = depth.astype(np.uint8)
#        cv.imshow('Depth image', depthImage)
 
        # quit program when 'esc' key is pressed
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            break
    
    cv.destroyAllWindows()
