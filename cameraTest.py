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
    #
    return array


def nothing(x):
    pass


# cv.namedWindow("mask")
# cv.createTrackbar("Hue", "mask", 0, 180, nothing)
# cv.createTrackbar("Saturation", "mask", 0, 255, nothing)
# cv.createTrackbar("Value", "mask", 0, 255, nothing)


if __name__ == "__main__":
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    orangeLower = (165, 200, 180)
    orangeUpper = (189, 255, 255)
    # [ -5 216 163] [ 15 236 243]
    # [-10 173 203] [ 10 193 283]
    # [169 212 191] [189 232 271]

    fgbg = cv.createBackgroundSubtractorMOG2()

    startup_counter = 0

    while startup_counter < 400:
        frame = get_video()
        depth = get_depth()
        startup_counter += 1
        print(startup_counter)

    while True:
        # orangeUpper = (cv.getTrackbarPos("Hue", "mask"),
        #                cv.getTrackbarPos("Saturation", "mask"),
        #                cv.getTrackbarPos("Value", "mask"))
        #frame = get_video()
        depth = get_depth()

        # Blur frame and convert to HSV color space
        # blurred = cv.GaussianBlur(frame, (11, 11), 0)
        # hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
        # mask = cv.inRange(hsv, orangeLower, orangeUpper)
        # mask = cv.erode(mask, None, iterations=2)
        # mask = cv.dilate(mask, None, iterations=2)

        #
        # cv.imshow('RGB image', frame)
        # cv.imshow('mask', mask)
        # display depth image
        # cv.line(depthImage, (40, 0), (40, 480), color=(0, 0, 255), thickness=2)
        # cv.line(depthImage, (600, 0), (600, 480), color=(0, 0, 255), thickness=2)
        # cv.line(depthImage, (0, 60), (640, 60), color=(0, 0, 255), thickness=2)
        # cv.line(depthImage, (0, 440), (640, 440), color=(0, 0, 255), thickness=2)
        # cv.imshow('Depth image', depthImage)

        # crop_frame = frame[60:480, 40:600]
        depth = depth[60:480, 40:600]
        depth = cv.GaussianBlur(depth, (11, 11), 0)
        # depth = cv.erode(depth, None, iterations=2)
        # depth = cv.dilate(depth, None, iterations=2)

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

            print("depth:", depth[center[1], center[0]])


        depthImage = depth.astype(np.uint8)
        # cv.imshow('crop', crop_frame)
        cv.imshow('depth', depthImage)
        cv.imshow('Foreground & Background Mask', fgmask)


        # quit program when 'esc' key is pressed
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord("p"):
            print("Capturing image...")
            cv.imwrite("testImage.jpg", frame)

cv.destroyAllWindows()
