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
        self.y = y_coord
        self.z = z_coord
        self.timestamp = timestamp
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
        
    def addPoint(self, p):
        self.points.append(p)
        
    def smooth(self):
        # Function to filter any outlying value in flight coordinates
        usable_pts = deque(maxlen=64)
        #print("Smoothed points:")
        for i in range(0, len(self.points)-1):
            point = self.points[i]
            # filter out any noisy/garbage depth data and estimate 
            if (point.z == 0) & (i > 0):
                point.z = usable_pts[i-1].z
            usable_pts.append(point)
            
            # Add the modified points to the flight
        self.points = usable_pts
        
    def relate_to_target(self, camera_height, target_x, target_y, target_z):
        a = 0.00173667 # The focal length of kinect camera
        for p in self.points:
            p.x = -target_x + int((p.x - 320) * a * p.z)
            p.y = camera_height + int((p.y - 240) * a * p.z)
            p.z = target_z - p.z
            print("Point:", p.x, p.y, p.z)
        
    def calculate_flight_data(self):
        # Function to parse flight coordinates into momentary horizontal 
        # and vertical velocities
        for i in range(len(self.points) - 2): # Dont perform on last point
            p1 = self.points[i]
            p2 = self.points[i+1]
            
            # Convert coordinates from pixels to real-world measurements (mm)
#            a = 0.00173667 # The focal length of kinect camera
#            camera_height = 1340 # Camera distance from the ground (mm)
#            
#            x1 = int((p1.x - 320) * a * p1.z)
#            x2 = int((p2.x - 320) * a * p2.z)  
#            y1 = int((p1.y - 240) * a * p1.z) + camera_height
#            y2 = int((p2.y - 240) * a * p2.z) + camera_height
            x1 = p1.x
            x2 = p2.x
            y1 = p1.y
            y2 = p2.y
            
            # Calculate the angle of flight between 2 points
            x_dist = x2 - x1
            y_dist = y2 - y1
            theta = math.degrees(math.atan(y_dist / x_dist))
            self.h_velocity_at_points.append(theta)
            
            # Calculate the flight distance between 2 points
            distance = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))
            self.distance_between_points.append(distance)
            
            # Calculate the projectiles velocities at each point
            time_diff = (p2.timestamp - p1.timestamp) / 1000 # seconds
            h_vel = (x_dist / 1000) / time_diff # meters/second
            v_vel = (y_dist / 1000) / time_diff # meters/second        
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
        self.ax = self.fig.add_subplot(111, projection = '3d')
        
        x_val = [p.x for p in self.points]
        y_val = [p.y for p in self.points]
        #y_val.reverse()
        z_val = [p.z for p in self.points]
        #The first depth value tends to be zero/garbage, so lets estimate it
        z_val[0] = z_val[1] - (z_val[2] - z_val[1])
        # Plot the graph
        self.ax.plot(x_val, y_val, z_val)
        self.ax.plot((x_val[-1], x_val[0]), (y_val[-1], y_val[-1]), (z_val[-1], z_val[0]))
        self.ax.plot([0.],[1240.],[0.], marker='X', markersize=10)
        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.set_zlabel("Z (meters)")
        self.ax.set_xlim(-3000, 0)
        self.ax.set_ylim(0, 2500)
        self.ax.set_zlim(-1250, 1250)
        # Set initial viewing angle
        self.ax.view_init(-90, -90)
        plt.show()
        
        
    
    
            
        