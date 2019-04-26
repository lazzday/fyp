#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 19:05:09 2019

@author: liam
"""

import math
import os
import time

import matplotlib
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

    def relate_to_target(self, camera_height, target_x, target_y, target_z):
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
        self.plot_number = 0

    def add_point(self, p):
        self.points.append(p)

    # Function to define complete list of points along predicted trajectory
    def generate_trajectory_points(self):
        z_val = np.array([p.z for p in self.points])
        x_val = np.array([p.x for p in self.points])
        y_val = np.array([p.y for p in self.points])

        # Use regression to find the best fit slope
        m = (((np.mean(x_val) * np.mean(z_val)) - np.mean(x_val * z_val)) /
             ((np.mean(x_val) * np.mean(x_val)) - np.mean(x_val * x_val)))
        b = np.mean(z_val) - m * np.mean(x_val)

        # Fit to a polynomial function (2nd degree = Quadratic)
        polynomial_coeffs = np.polyfit(x_val, y_val, 2)
        # print("Polynomial Function: y = {} + {}x + {}x^2".format(polynomial_coeffs[0],
        #       polynomial_coeffs[1],
        #       polynomial_coeffs[2]))

        # Function for the curve: y = a + bx^1 + cx^2
        def curve_function(x):
            y = polynomial_coeffs[2] + polynomial_coeffs[1] * x + polynomial_coeffs[0] * math.pow(x, 2)
            return y

        x_range = np.arange(x_val[-1], 0, -x_val[0]/10)

        for predicted_x in x_range:
            predicted_y = curve_function(predicted_x)
            predicted_z = (m * predicted_x) + b
            # print("Predicted Point:", predicted_x, predicted_y, predicted_z)
            self.trajectory.append([predicted_x, predicted_y, predicted_z])

    # Function to define the last point of the trajectory, the point of impact
    def predict_final_point(self, TARGET_CENTER_HEIGHT):
        z_val = np.array([p.z for p in self.points])
        x_val = np.array([p.x for p in self.points])
        y_val = np.array([p.y for p in self.points])

        # Use regression to find the best fit slope
        m = (((np.mean(x_val) * np.mean(z_val)) - np.mean(x_val * z_val)) /
             ((np.mean(x_val) * np.mean(x_val)) - np.mean(x_val * x_val)))
        b = np.mean(z_val) - m * np.mean(x_val)

        # Fit to a polynomial function (2nd degree = Quadratic)
        polynomial_coeffs = np.polyfit(x_val, y_val, 2)
        # print("Polynomial Function: y = {} + {}x + {}x^2".format(polynomial_coeffs[0],
        #                                                          polynomial_coeffs[1],
        #                                                          polynomial_coeffs[2]))

        # Function for the curve: y = a + bx^1 + cx^2
        def curve_function(x):
            y = polynomial_coeffs[2] + polynomial_coeffs[1] * x + polynomial_coeffs[0] * math.pow(x, 2)
            return y

        x_at_target = 0
        y_at_target = TARGET_CENTER_HEIGHT
        self.predicted_point_of_impact = [x_at_target, curve_function(x_at_target), (m * x_at_target) + b]
        return [x_at_target, curve_function(x_at_target) - y_at_target, (m * x_at_target) + b]

    def plot(self):
        matplotlib.use('Agg')

        # Function to plot the flight on a 3D graph
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_val = [p.x for p in self.points]
        y_val = [p.y for p in self.points]
        z_val = [p.z for p in self.points]
        ax.plot(x_val, y_val, z_val, label="Detected")

        predicted_x_val = [p[0] for p in self.trajectory]
        predicted_y_val = [p[1] for p in self.trajectory]
        predicted_z_val = [p[2] for p in self.trajectory]
        ax.scatter(predicted_x_val, predicted_y_val, predicted_z_val, label="Predicted")

        # ax.plot([0.], [self.], [0.], marker='X', markersize=10)
        ax.plot([self.predicted_point_of_impact[0]],
                [self.predicted_point_of_impact[1]],
                [self.predicted_point_of_impact[2]],
                marker='X', markersize=10)
        # ax.set_xlabel("X (mm)")
        # ax.set_ylabel("Y (mm)")
        # ax.set_zlabel("Z (mm)")
        ax.set_xlim(-1750, 0)
        ax.set_ylim(2000, 0)
        ax.set_zlim(-1000, 1000)

        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        ax.zaxis.set_ticklabels([])


        # Set initial viewing angle
        ax.view_init(azim=270, elev=-60)
        # plt.legend(loc='upper left')
        # plt.show()
        folder = "images/plots"
        plot_name = "throw{}.png".format(self.plot_number)
        self.plot_number += 1
        fig.savefig(os.path.join(folder, plot_name), transparent=True)

    def clearup(self):
        self.points.clear()
        self.trajectory.clear()

    # Function to get current time in millseconds (for timers)
    def get_time_millis(self):
        return int(round(time.time() * 1000))