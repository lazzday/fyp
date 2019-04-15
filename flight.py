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
        self.y = 420 - y_coord
        self.z = z_coord
        self.timestamp = timestamp

    def relate_to_target(self, camera_height=1340, target_x=1940, target_y=0, target_z=1225):
        # Function to convert point coordinates to real-world distances,
        # relative to the target area.
        a = 0.00173667  # The focal length of kinect camera

        self.x = -target_x + int((self.x - 270) * a * self.z)
        self.y = camera_height + int((self.y - 210) * a * self.z)
        self.z = 0 - target_z + self.z
        print("Point:", self.x, self.y, self.z, self.timestamp)
#        print("Point:", self.x, self.y, self.z)

class RecordedFlight:
    # A class for a complete set of RecordedPoint objects to analyze 
    # of projectile.

    def __init__(self):
        self.points = deque(maxlen=64)
        self.angles_of_flight = deque(maxlen=64)
        self.h_velocity_at_points = deque(maxlen=64)
        self.v_velocity_at_points = deque(maxlen=64)
        self.distance_between_points = deque(maxlen=64)

    def add_point(self, p):
        self.points.append(p)

    def smooth(self):
        # Function to filter any outlying value in flight coordinates
        usable_pts = deque(maxlen=64)
        # print("Smoothed points:")
        for i in range(0, len(self.points) - 1):
            point = self.points[i]
            # filter out any noisy/garbage depth data and estimate
            if (point.z == 0) & (i > 0):
                point.z = usable_pts[i - 1].z
            # filter out any point with outlying x value that suggest the ball is moving backwards
            if (point.x < self.points[i + 1].x) & (i < len(self.points) - 1):
                usable_pts.append(point)

            # Add the modified points to the flight
        self.points = usable_pts

    def calculate_flight_data(self):
        # Function to parse flight coordinates into momentary horizontal 
        # and vertical velocities
        for i in range(len(self.points) - 2):  # Dont perform on last point
            p1 = self.points[i]
            p2 = self.points[i + 1]

            x1 = p1.x
            x2 = p2.x
            y1 = p1.y
            y2 = p2.y

            # Calculate the angle of flight between 2 points
            x_dist = x2 - x1
            y_dist = y2 - y1
            #            theta = math.degrees(math.atan(y_dist / x_dist))
            #            self.angles_of_flight.append(theta)

            # Calculate the flight distance between 2 points
            distance = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))
            self.distance_between_points.append(distance)

            # Calculate the projectiles velocities at each point
            time_diff = (p2.timestamp - p1.timestamp) / 1000  # seconds
            h_vel = (x_dist / 1000) / time_diff  # meters/second
            v_vel = (y_dist / 1000) / time_diff  # meters/second
            self.h_velocity_at_points.append(h_vel)
            self.v_velocity_at_points.append(v_vel)

        print("Total time: "
              + str((self.points[-1].timestamp - self.points[0].timestamp) / 1000)
              + "seconds")
        print("Total Horizontal Distance: "
              + str((self.points[-1].x - self.points[0].x) / 1000)
              + "meters")
        print("Total Arc Distance: "
              + str(sum(self.distance_between_points) / 1000)
              + "meters")
        print("Average Horizontal Velocity = "
              + str(np.mean(self.h_velocity_at_points))
              + "m/s")

    def plot(self):
        # Function to plot the flight on a 3D graph
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        x_val = [p.x for p in self.points]
        y_val = [p.y for p in self.points]
        z_val = [p.z for p in self.points]
        # The first depth value tends to be zero/garbage, so lets estimate it
        # z_val[0] = z_val[1] - (z_val[2] - z_val[1])
        # Plot the graph
        self.ax.plot(x_val, y_val, z_val)
        self.ax.plot((x_val[-1], x_val[0]), (y_val[-1], y_val[-1]), (z_val[-1], z_val[0]))
        self.ax.plot([0.], [1240.], [0.], marker='X', markersize=10)
        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.set_zlabel("Z (meters)")
        self.ax.set_xlim(-3000, 0)
        self.ax.set_ylim(2500, 0)
        self.ax.set_zlim(-1250, 1250)
        # Set initial viewing angle
        self.ax.view_init(-90, -90)
        plt.show()

#    def time_of_flight(self):
#        v_i_v = v_velocity_at_points[1]
#        if v_i_v > 0: # Projectile is ascending
#            #code
#        else: # Projectile is descending
#            #code
#            
#        
#        
#        
#        h_i_v = h_velocity_at_points[1]
#        t_up = v_i_v / 9.8
#        h_range = h_i_v *
