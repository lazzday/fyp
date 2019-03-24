#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 19:05:09 2019

@author: liam
"""

import math

class RecordedPoint:
    
    def __init__(self, x_coord, y_coord, z_coord, timestamp):
        self.x = x_coord
        self.y = y_coord
        self.z = z_coord
        self.timestamp = timestamp
        print("Point:", self.x, self.y, self.z)
        
    def point_in_meters(self):
        # Kinect only records x and y coordinates in terms of pixels
        # To convert to real world distance (meters) we mus apply the following
        # calculations:
        #
        #   x = (i - 320) * a * z
        #   y = (j - 240) * a * z
        #
        # where i and j are the recorded point in terms of pixels
        # and a is the known focal length of the kinect:
        #   a = 0.00173667meters
        
        a = 0.00173667 # The focal length of kinect camera
        self.x = (self.x - 320) * a * self.z
        self.y = (self.y - 240) * a * self.z
    
    def save_point():
        
class RecordedFlight:
    # A class for a complete set of RecordedPoint objects to analyze 
    # of projectile.
    
    def __init__(self):
        self.points = deque(maxlen=64)
        self.angles_of_flight = deque(maxlen=64)
        self.h_velocity_at_points = deque(maxlen=64)
        self.v_velocity_at_points = deque(maxlen=64)
        self.distance_between_points = deque(maxlen=64)
        
    def addPoint(self,p):
        self.points.append(p)
        
    def calculate_flight_data(self):
        # Function to parse flight coordinates into momentary horizontal 
        # and vertical velocities
        g = 9800 # acceleration due to gravity (mm/s)
        for i in range(len(self.points) - 2): # Dont perform on last point
            # Calculate the angle of flight between 2 points
            p1 = points[i]
            p2 = points[i+1]
            x_dist = p2.x - p1.x
            y_dist = p2.y - p2.y
            theta = math.degrees(math.atan(y_dist / x_dist))
            self.velocity_at_points.append(theta)
            
            # Calculate the flight distance between 2 points
            distance = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))
            self.distance_between_points(distance)
            
            # Calculate the projectiles velocities at each point
            time_diff = (p2.timestamp - p1.timestamp) / 1000 # seconds
            h_vel = (x_dist / 1000) / time_diff # meters/second
            v_vel = (y_dist / 1000) / time_diff # meters/second        
            self.h_velocity_at_points.append(h_vel)
            self.v_velocity_at_points.append(v_vel)
            
    
    
            
        