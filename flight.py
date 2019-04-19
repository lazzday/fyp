#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 19:05:09 2019

@author: liam
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from mpl_toolkits.mplot3d import axes3d


class RecordedPoint:

    def __init__(self, x_coord, y_coord, z_coord, timestamp):
        # Convert x,y in pixels to real world distance (mm)
        self.x = x_coord
        self.y = 480 - y_coord
        self.z = z_coord
        self.timestamp = timestamp

    def relate_to_target(self, camera_height=1340, target_x=1940, target_y=0, target_z=1225):
        # Function to convert point coordinates to real-world distances,
        # relative to the target area.
        a = 0.00173667  # The focal length of kinect camera

        self.x = -target_x + int((self.x - 320) * a * self.z)
        self.y = camera_height + int((self.y - 240) * a * self.z)
        self.z = 0 - target_z + self.z
        print("Point:", self.x, self.y, self.z, self.timestamp)


class RecordedFlight:
    # A class for a complete set of RecordedPoint objects to analyze 
    # of projectile.

    def __init__(self):
        self.points = deque(maxlen=64)
        self.trajectory = deque(maxlen=64)

    def add_point(self, p):
        self.points.append(p)

    def predict_trajectory(self):
        z_val = np.array([p.z for p in self.points])
        x_val = np.array([p.x for p in self.points])
        y_val = np.array([p.y for p in self.points])

        # Use regression to find the best fit slope
        m = (((np.mean(x_val) * np.mean(z_val)) - np.mean(x_val * z_val)) /
             ((np.mean(x_val) * np.mean(x_val)) - np.mean(x_val * x_val)))
        b = np.mean(z_val) - m * np.mean(x_val)

        # Fit to a polynomial function (2nd degree = Quadratic)
        polynomial_coeffs = np.polyfit(x_val, y_val, 2)
        print("Polynomial Function: y = {} + {}x + {}x^2".format(polynomial_coeffs[0],
              polynomial_coeffs[1],
              polynomial_coeffs[2]))

        # Function for the curve: y = a + bx^1 + cx^2
        def curve_function(x):
            y = polynomial_coeffs[2] + polynomial_coeffs[1] * x + polynomial_coeffs[0] * math.pow(x, 2)

            return y

        x_range = np.arange(x_val[-1], 0, -x_val[0]/10)

        for predicted_x in x_range:
            predicted_y = curve_function(predicted_x)
            predicted_z = (m * predicted_x) + b
            print("Predicted Point:", predicted_x, predicted_y, predicted_z)
            self.trajectory.append([predicted_x, predicted_y, predicted_z])

    def plot(self):
        # Function to plot the flight on a 3D graph
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_val = [p.x for p in self.points]
        y_val = [p.y for p in self.points]
        z_val = [p.z for p in self.points]
        ax.plot(x_val, y_val, z_val)

        predicted_x_val = [p[0] for p in self.trajectory]
        predicted_y_val = [p[1] for p in self.trajectory]
        predicted_z_val = [p[2] for p in self.trajectory]
        ax.scatter(predicted_x_val, predicted_y_val, predicted_z_val)

        ax.plot([0.], [1000.], [0.], marker='X', markersize=10)
        ax.set_xlabel("X (meters)")
        ax.set_ylabel("Y (meters)")
        ax.set_zlabel("Z (meters)")
        ax.set_xlim(-3000, 0)
        ax.set_ylim(2500, 0)
        ax.set_zlim(-1250, 1250)
        # Set initial viewing angle
        ax.view_init(-90, -90)
        plt.show()

