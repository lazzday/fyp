# import the necessary modules
import freenect
import cv2 as cv
import numpy as np
from collections import deque
import imutils
from calibReader import CalibReader
import time
from flight import RecordedPoint, RecordedFlight
from utils import FrameSave


# function to get RGB image from kinect
def get_video():
    array, _ = freenect.sync_get_video()
    # Crop to usable space:
    array = array[60:480, 40:600]
    array = cv.cvtColor(array, cv.COLOR_RGB2BGR)
    return array


# function to get depth image from kinect
def get_depth():
    array, _ = freenect.sync_get_depth(format=freenect.DEPTH_REGISTERED)
    # Crop to usable space:
    array = array[60:480, 40:600]
    return array


# Function to compute stereo rectification maps
def compute_rect_maps(ir_mat, ir_dist, rgb_mat, rgb_dist, trans_vec, rot_mat):
    imgSize = (640, 480)
    rotation1, rotation2, pose1, pose2, q, roi1, roi2 = cv.stereoRectify(
        cameraMatrix1=ir_mat,
        distCoeffs1=ir_dist,
        cameraMatrix2=rgb_mat,
        distCoeffs2=rgb_dist,
        imageSize=imgSize,
        R=rot_mat,
        T=trans_vec,
        flags=cv.CALIB_ZERO_DISPARITY,
        newImageSize=imgSize)

    ir_map_x, ir_map_y = cv.initUndistortRectifyMap(ir_mat,
                                                    ir_dist,
                                                    rotation1,
                                                    pose1,
                                                    imgSize,
                                                    cv.CV_32FC1)

    rgb_map_x, rgb_map_y = cv.initUndistortRectifyMap(rgb_mat,
                                                      rgb_dist,
                                                      rotation2,
                                                      pose2,
                                                      imgSize,
                                                      cv.CV_32FC1)

    return ir_map_x, ir_map_y, rgb_map_x, rgb_map_y


# Function to get current time in millseconds (for timers)
def get_time_millis():
    return int(round(time.time() * 1000))


# Function to remap moth frames using maps generated by compute_rect_maps()
def remap_frame(ir_frame, rgb_frame, ir_map_x, ir_map_y, rgb_map_x, rgb_map_y):
    ir_remapped = cv.remap(src=ir_frame,
                           map1=ir_map_x,
                           map2=ir_map_y,
                           interpolation=cv.INTER_LINEAR)
    rgb_remapped = cv.remap(src=rgb_frame,
                            map1=rgb_map_x,
                            map2=rgb_map_y,
                            interpolation=cv.INTER_LINEAR)
    return ir_remapped, rgb_remapped


if __name__ == "__main__":

    # Set green thresholds in HSV
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)
    # Initialize list of tracked points
    pts = deque(maxlen=64)
    recorded_flight = RecordedFlight()

    # Parse the calib.ini file and load into stereo rectifier
    rel_path = "/home/liam/fyp/calib/kinect_calib_values/calib.ini"

    calib_reader = CalibReader(rel_path)
    ir_camera_mat, ir_dist_coeffs = calib_reader.get_IR_calib()
    rgb_camera_mat, rgb_dist_coeffs = calib_reader.get_RGB_calib()
    translation_vector, rotation_matrix = calib_reader.get_stereo_calib()

    irMapX, irMapY, rgbMapX, rgbMapY = compute_rect_maps(ir_camera_mat,
                                                         ir_dist_coeffs,
                                                         rgb_camera_mat,
                                                         rgb_dist_coeffs,
                                                         translation_vector,
                                                         rotation_matrix)

    # Start timer for velocity calculations and framerate calculation
    start_time = get_time_millis()
    frames_captured = 0

    # Booleans to determine successful projectile capture
    projectile_in_view = False
    flight_recorded = False

    # Clear the capturedFrames folder
    FrameSave.clear_capture_folder()
    frame_count = 0

    while True:

        # When flight is captured successfully
        if (projectile_in_view == False) & (flight_recorded == True):
            print("Projectile flight captured successfully")
            break
        # Get RGB video frame
        frame = get_video()
        # Get Depth Sensor frame
        depth = get_depth()

        frames_captured += 1

        # Blur frame and convert to HSV color space
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        # Create mask for green/yellow color of ball
        mask = cv.inRange(hsv, greenLower, greenUpper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        # Find contours in mask
        contours = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
                                   cv.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # Center of ball
        ballCenter = None
        # At least one contour is found
        if len(contours) > 0:
            # Find largest contour and compute enclosing circle and centroid
            c = max(contours, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # Radius meets a minimum size
            if radius > 5:
                # Draw circle around the ball
                cv.circle(frame, (int(x), int(y)), int(radius),
                          (0, 255, 255), 2)
                cv.circle(depth, (int(x), int(y)), int(radius),
                          (0, 255, 255), 2)
                # Draw the center point of the ball
                cv.circle(frame, center, 5, (0, 0, 255), -1)

                depthValue = depth.item(int(y), int(x))
                point_time = get_time_millis() - start_time
                point = RecordedPoint(int(x), int(y), depthValue, point_time)
                point.relate_to_target()
                recorded_flight.add_point(point)
                projectile_in_view = True
                flight_recorded = True
                # Save frame to folder
                FrameSave.save_frame(frame, depth, frame_count)
                frame_count += 1
        else:
            projectile_in_view = False

        cv.imshow('RGB image', frame)
        # display depth image
        depthImage = depth.astype(np.uint8)
        cv.imshow('Depth image', depthImage)

        # quit program when 'esc' key is pressed
        k = cv.waitKey(1) & 0xFF
        if k == ord("q"):
            break
    # While loop is broken  
    cv.destroyAllWindows()
    total_time = (get_time_millis() - start_time) / 1000
    fps = int(frames_captured / total_time)
    print("Points captured:", len(recorded_flight.points))
    print("Frames per second:", fps)
    recorded_flight.smooth()
    recorded_flight.plot()
    recorded_flight.calculate_flight_data()
    print("Horizontal Velocities:", recorded_flight.h_velocity_at_points)
#    print("Average Horizontal Velocity:", np.mean(recorded_flight.h_velocity_at_points))
