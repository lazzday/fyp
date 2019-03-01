# -*- coding: utf-8 -*-
"""
Class to parse .ini calibration file generated by MRPT kinect-stereo-calib
"""
from configparser import ConfigParser
import numpy as np

class CalibReader:
    
    def __init__(self, calib_file_path):
        # Open the calibration file
        self.config = ConfigParser()
        self.config.read(calib_file_path)
        
    # Parse the Depth Camera intrinsics
    def get_IR_calib(self):
        
        cx = self.config.getfloat('CAMERA_PARAMS_LEFT', 'cx')
        cy = self.config.getfloat('CAMERA_PARAMS_LEFT', 'cy')
        fx = self.config.getfloat('CAMERA_PARAMS_LEFT', 'fx')
        fy = self.config.getfloat('CAMERA_PARAMS_LEFT', 'fy')
        dist = self.config.get('CAMERA_PARAMS_LEFT', 'dist')
        
        cameraMatrix = np.matrix([[fx, 0, cx],
                                 [0, fy, cy],
                                 [0, 0, 1]])
        
        distCoeffs = np.fromstring(dist, dtype=float, sep=' ')
        
        return cameraMatrix, distCoeffs
   
    # Parse the RGB Camera intrinsics
    def get_RGB_calib(self):
        cx = self.config.getfloat('CAMERA_PARAMS_RIGHT', 'cx')
        cy = self.config.getfloat('CAMERA_PARAMS_RIGHT', 'cy')
        fx = self.config.getfloat('CAMERA_PARAMS_RIGHT', 'fx')
        fy = self.config.getfloat('CAMERA_PARAMS_RIGHT', 'fy')
        dist = self.config.get('CAMERA_PARAMS_RIGHT', 'dist')
        
        cameraMatrix = np.matrix([[fx, 0, cx],
                                 [0, fy, cy],
                                 [0, 0, 1]])
        
        distCoeffs = np.fromstring(dist, dtype=float, sep=' ')
        
        return cameraMatrix, distCoeffs
    
    # Parse the stereo calibration extrinsics
    def get_stereo_calib(self):
        trans = self.config.get('CAMERA_PARAMS_LEFT2RIGHT_POSE', 
                                'translation_only')
        translation_vector = np.fromstring(trans, dtype=float, sep=' ')
        
        rot = self.config.get('CAMERA_PARAMS_LEFT2RIGHT_POSE',
                              'rotation_matrix_only')
        rotation_vector = np.fromstring(rot, dtype=float, sep=' ')
        rotation_matrix = np.reshape(rotation_vector, (3, 3))
        
        return translation_vector, rotation_matrix