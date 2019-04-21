from multiprocessing import Manager, Queue

import animation
import projectileDetector


with Manager() as manager:
    namespace = manager.Namespace()

    namespace.done = False
    queue = manager.Queue()

    jobs = [
        animation.Animation(namespace, queue),
        projectileDetector.ProjectileDetector(namespace, queue),
    ]

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()