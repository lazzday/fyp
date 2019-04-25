from multiprocessing import Manager, Queue

import animation
import projectileDetector
import dartboardGame

CAMERA_HEIGHT = 1280  # The height of the camera in mm
CAMERA2TARGET_X = 1300  # The perpendicular x distance from camera to target in mm
CAMERA2TARGET_Z = 940  # The z (depth) distance from camera to target centerpoint in mm
TARGET_CENTER_HEIGHT = 1170  # The real-world height of the center of the target in mm

SCREEN_WIDTH = 1310  # The target display width in mm
SCREEN_HEIGHT = 960  # The target display width in mm


with Manager() as manager:
    namespace = manager.Namespace()

    namespace.done = False
    queue = manager.Queue()

    jobs = [
        # animation.Animation(namespace, queue),
        projectileDetector.ProjectileDetector(namespace,
                                              queue,
                                              CAMERA_HEIGHT,
                                              CAMERA2TARGET_X,
                                              CAMERA2TARGET_Z,
                                              TARGET_CENTER_HEIGHT),
        dartboardGame.DartboardGame(namespace, queue,
                                    SCREEN_WIDTH,
                                    SCREEN_HEIGHT)
    ]

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()