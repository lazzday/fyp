# import the necessary modules
import freenect
import cv2 as cv
import numpy as np
from collections import deque
import imutils
import time
from flight import RecordedPoint, RecordedFlight
from utils import FrameSave
import multiprocessing


class ProjectileDetector(multiprocessing.Process):

    def __init__(self, the_state, queue,
                 CAMERA_HEIGHT,
                 CAMERA2TARGET_X,
                 CAMERA2TARGET_Z,
                 TARGET_CENTER_HEIGHT):
        super(ProjectileDetector, self).__init__()
        self.queue = queue

        self.CAMERA_HEIGHT = CAMERA_HEIGHT
        self.CAMERA2TARGET_X = CAMERA2TARGET_X
        self.CAMERA2TARGET_Z = CAMERA2TARGET_Z
        self.TARGET_CENTER_HEIGHT = TARGET_CENTER_HEIGHT

        FrameSave.clear_images()

    # function to get RGB image from kinect
    def get_video(self):
        array, _ = freenect.sync_get_video()
        # Crop to usable space:
        array = array[60:480, 40:600]
        array = cv.cvtColor(array, cv.COLOR_RGB2BGR)
        latency_start = start_time - get_time_millis()
        return array, latency_start

    # function to get depth image from kinect
    def get_depth(self):
        array, _ = freenect.sync_get_depth(format=freenect.DEPTH_MM)
        return array

    # Function to get current time in millseconds (for timers)
    def get_time_millis(self):
        return int(round(time.time() * 1000))

    # if __name__ == "__main__":
    def run(self):
        # Initialize list of tracked points
        pts = deque(maxlen=64)
        recorded_flight = RecordedFlight()

        # Deque of frames to save as images
        images_to_save = deque(maxlen=64)
        mask_frames = deque(maxlen=64)

        # Start timer for velocity calculations and framerate calculation
        start_time = self.get_time_millis()
        frames_captured = 0

        # Booleans to determine successful projectile capture
        projectile_in_view = False
        flight_recorded = False
        look_for_contours = False
        depth_image_settled = False

        # Clear the capturedFrames folder
        FrameSave.clear_capture_folder()
        frame_count = 0

        # Background Subtraction setup
        fgbg = cv.createBackgroundSubtractorMOG2(varThreshold=144)

        # Wait until depth image has settled so no false positives are detected
        settle_timer = self.get_time_millis()
        print("Waiting depth image to settle...")
        while not depth_image_settled:
            depth = self.get_depth()
            if self.get_time_millis() - settle_timer > 30000:
                depth_image_settled = True
                look_for_contours = True
                print("Ready to detect projectiles!")
                self.queue.put("Ready")

        throws_detected = 0
        # while throws_detected < 3:
        while True:
            projectile_in_view = False
            flight_recorded = False
            recorded_flight.clearup()
            mask_frames.clear()

            while True:
                # When flight is captured successfully
                if (projectile_in_view == False) & (flight_recorded == True):
                    print("Projectile flight captured successfully")
                    break

                # Get Depth Sensor frame
                depth = self.get_depth()

                frames_captured += 1

                # Apply blur to filter out random IR noise
                # depth = cv.GaussianBlur(depth, (11, 11), 0)

                # apply background substraction
                fgmask = fgbg.apply(depth)
                contours = cv.findContours(fgmask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)

                # Ignore the first frame it gives a false positive
                if frames_captured < 10:
                    continue

                # Center of ball
                ballCenter = None

                if look_for_contours == True:
                    for c in contours:
                        if cv.contourArea(c) < 1000:
                            continue
                        ((x, y), radius) = cv.minEnclosingCircle(c)
                        M = cv.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                        cv.circle(depth, (int(x), int(y)), int(radius), (0, 255, 255), 2)

                        depthValue = depth.item(center[1], center[0])
                        if center[0] > depth.shape[1] - 100:
                            projectile_in_view = False
                            continue
                        elif depthValue != 0:
                            point_time = self.get_time_millis() - start_time
                            point = RecordedPoint(center[0], center[1], depthValue, point_time)
                            point.relate_to_target(self.CAMERA_HEIGHT,
                                                   self.CAMERA2TARGET_X,
                                                   self.TARGET_CENTER_HEIGHT,
                                                   self.CAMERA2TARGET_Z)
                            recorded_flight.add_point(point)
                            projectile_in_view = True
                            flight_recorded = True
                            # Save frame to folder
                            images_to_save.append(depth.astype(np.uint8))
                            mask_frames.append(fgmask)
                            frame_count += 1

                # cv.imshow('RGB image', frame)
                # display depth image

                # depthImage = depth.astype(np.uint8)
                # cv.imshow("depth", depthImage)

                # quit program when 'esc' key is pressed
                k = cv.waitKey(1) & 0xFF
                if k == ord("q"):
                    break


        # While loop is broken
            total_time = (self.get_time_millis() - start_time) / 1000
            fps = int(frames_captured / total_time)
            print("Points captured:", len(recorded_flight.points))
            print("Frames per second:", fps)
            point_of_impact = recorded_flight.predict_final_point(self.TARGET_CENTER_HEIGHT)
            print("Sending to queue")
            self.queue.put(point_of_impact)
            recorded_flight.generate_trajectory_points()
            # FrameSave.save_frames(images_to_save)
            FrameSave.generate_flight_mask_image(mask_frames, throws_detected)
            throws_detected += 1
            recorded_flight.plot()

            k = cv.waitKey(1) & 0xFF
            if k == ord("q"):
                break
        # print("Average Latency between RGB - Depth: ", np.mean(avg_latency))
    #    print("Average Horizontal Velocity:", np.mean(recorded_flight.h_velocity_at_points))

        cv.destroyAllWindows()
