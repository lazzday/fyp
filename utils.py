'''
Utility functions and classes for projectileDetector.py
for saving captured frames.

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
    def save_frames(depth_frames):
        folder = 'capturedFrames/depth'
        if not os.path.exists(folder):
            os.mkdir(folder)

        count = 0
        for f in depth_frames:
            file = "frame{:d}.jpg".format(count)
            cv.imwrite(os.path.join(folder, file), f)
            count += 1

    @staticmethod
    def generate_flight_mask_image(mask_frames, saveCount):
        overlay_image = mask_frames[0]
        for f in mask_frames:
            overlay_image = cv.add(overlay_image, f)
        cv.imwrite(os.path.join("images/flightMasks", "throw{}.jpg".format(saveCount)), overlay_image)

    @staticmethod
    def clear_images():
        folder = 'images/plots'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        folder = 'images/flightMasks'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)