'''
Main class of project that initialise the projectile detector and game processes
'''



from multiprocessing import Manager, Queue

import projectileDetector
import dartboardGame

CAMERA_HEIGHT = 1270  # The height of the camera in mm
CAMERA2TARGET_X = 1270  # The perpendicular x distance from camera to target in mm
CAMERA2TARGET_Z = 930  # The z (depth) distance from camera to target centerpoint in mm
TARGET_CENTER_HEIGHT = 1165  # The real-world height of the center of the target in mm
SCREEN_WIDTH = 1190  # The target display width in mm
SCREEN_HEIGHT = 895  # The target display width in mm

with Manager() as manager:
    namespace = manager.Namespace()

    namespace.done = False
    queue = manager.Queue()

    jobs = [
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