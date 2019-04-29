#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Simple script to test the viewing position of the camera for setup purposes
Red lines show the 3d-point recording thresholds 
'''

import freenect
import cv2 as cv
import imutils
import numpy as np

# function to get RGB image from kinect
def get_video():
    array, _ = freenect.sync_get_video()
    array = cv.cvtColor(array, cv.COLOR_RGB2BGR)
    return array


# function to get depth image from kinect
def get_depth():
    array, _ = freenect.sync_get_depth(format=freenect.DEPTH_MM)
    # array, _ = freenect.sync_get_depth()

    #
    return array


def nothing(x):
    pass


if __name__ == "__main__":


    fgbg = cv.createBackgroundSubtractorMOG2(varThreshold=144)

    depth = get_depth()
    depthImage = depth.astype(np.uint8)

    size = (depthImage.shape[1], depthImage.shape[0])
    print(depthImage.shape)

    # fourcc = cv.VideoWriter_fourcc(*'XVID')
    # out = cv.VideoWriter('testDepthFlight.avi', fourcc, 20.0, size)
    # out2 = cv.VideoWriter('testFGBGFlight.avi', fourcc, 20.0, size)
    # out3 = cv.VideoWriter('testRGBFlight.avi', fourcc, 20.0, size)



    while True:

        depth = get_depth()
        frame = get_video()

        # apply background substraction
        fgmask = fgbg.apply(depth)
        contours = cv.findContours(fgmask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # looping for contours
        for c in contours:
            if cv.contourArea(c) < 1000:
                continue

            # get bounding box from countour
            # (x, y, w, h) = cv.boundingRect(c)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # draw bounding box
            #     cv.rectangle(depth, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.circle(depth, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)


            print("depth:", depth[center[1], center[0]])

        depthImage = depth.astype(np.uint8)
        # cv.imshow('crop', crop_frame)
        cv.imshow('depth', depthImage)
        cv.imshow('Foreground & Background Mask', fgmask)

        depthImage = cv.cvtColor(depthImage, cv.COLOR_GRAY2BGR)
        fgmask = cv.cvtColor(fgmask, cv.COLOR_GRAY2BGR)
        # frame = cv.cvtColor(frame, cv.COLOR_2BGR)


        # out.write(depthImage)
        # out2.write(fgmask)
        # out3.write(frame)

        # quit program when 'esc' key is pressed
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord("p"):
            print("Capturing image...")
            cv.imwrite("testImage.jpg", frame)


cv.destroyAllWindows()


