#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 20:16:24 2019

@author: liam
"""

import cv2
import numpy as np
 
# Create a VideoCapture object
capL = cv2.VideoCapture(0)
capR = cv2.VideoCapture(1)
 
# Check if camera opened successfully
if (capL.isOpened() == False | capR.isOpened() == False): 
  print("Unable to read camera feed")
 
# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width = int(capL.get(3))
frame_height = int(capL.get(4))
 
# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
outL = cv2.VideoWriter('left.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
outR = cv2.VideoWriter('right.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

while(True):
  retL, frameL = capL.read()
  retR, frameR = capR.read()
  if retL == True & retR ==True: 
     
    # Write the frame into the file 'output.avi'
    outL.write(frameL)
    outR.write(frameR)
 
    # Display the resulting frame    
    cv2.imshow('left',frameL)
    cv2.imshow('right',frameR)
 
    # Press Q on keyboard to stop recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
 
  # Break the loop
  else:
    break 
 
# When everything done, release the video capture and video write objects
capL.release()
capR.release()
outL.release()
outR.release()
# Closes all the frames
cv2.destroyAllWindows() 