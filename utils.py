'''
Utility functions and classes for main.py
'''

import os
import shutil

import cv2 as cv

# Static class for handling saved frames as images
class FrameSave:

    @staticmethod
    def clear_capture_folder():
        folder = 'capturedFrames'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete subdirectories
            except Exception as e:
                print(e)

    @staticmethod
    def save_frame(frame, depth, frame_count):

        folder = 'capturedFrames/rgb'
        if not os.path.exists(folder):
            os.mkdir(folder)
        file = "frame{:d}.jpg".format(frame_count)
        cv.imwrite(os.path.join(folder, file), frame)
        folder = 'capturedFrames/depth'
        if not os.path.exists(folder):
            os.mkdir(folder)
        file = "frame{:d}.jpg".format(frame_count)
        cv.imwrite(os.path.join(folder, file), depth)


