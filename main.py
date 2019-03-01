#import the necessary modules
import freenect
import cv2 as cv
import numpy as np
from collections import deque
import os
import imutils
from configparser import ConfigParser
from calibReader import CalibReader


 
#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv.cvtColor(array,cv.COLOR_RGB2BGR)
    return array
 
#function to get depth image from kinect
def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array
 
if __name__ == "__main__":
    
    # Set green thresholds in HSV
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    # Initialize list of tracked points
    pts = deque(maxlen=64)
    
    # Parse the calib.ini file and load into stereo rectifier
    rel_path = "/home/liam/fyp/calib/kinect_calib_values/calib.ini"
    print(rel_path)
    
    calib_reader = CalibReader(rel_path)
    ir_camera_mat, ir_dist_coeffs = calib_reader.get_IR_calib()   
    rgb_camera_mat, rgb_dist_coeffs = calib_reader.get_RGB_calib()
    translation_vector, rotation_matrix = calib_reader.get_stereo_calib()

        
    while 1:
        # Get RGB video frame
        frame = get_video()
        # Get Depth Sensor frame
        depth = get_depth()
        
        # Blur frame and convert to HSV color space
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
        
        # Create mask for green/yellow color of ball
        mask = cv.inRange(hsv, greenLower, greenUpper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        
        # Find contours in mask
        contours = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
                                   cv.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        
        # Center of ball
        ballCenter = None
        
        # At least one contour is found
        if len(contours) > 0:
            # Find largest contour and compute enclosing circle and centroid
            c = max(contours, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            # Raduis meets a minimum size
            if radius > 10:
                # Draw circle around the ball
                cv.circle(frame, (int(x), int(y)), int(radius),
                          (0, 255, 255), 2)
                cv.circle(depth, (int(x), int(y)), int(radius),
                          (0, 255, 255), 2)
                # Draw the center point of the ball
                cv.circle(frame, center, 5, (0, 0, 255), -1)
                cv.circle(depth, center, 5, (0, 0, 255), -1)
                
            # Save the center to tracked pints queue
            pts.appendleft(center)
            
        
    
        cv.imshow('RGB image',frame)
        #display depth image
        cv.imshow('Depth image',depth)
 
        # quit program when 'esc' key is pressed
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            break
    cv.destroyAllWindows()