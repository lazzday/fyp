'''
***************************************
Liam Day
Bachelor of Engineering (Honours) in Software & Electronic Engineering
GMIT
2019
Final Year Project: 
Projectile Detection and Interaction
***************************************
'''

import cv2 as cv
import numpy as np
import freenect

def get_video():
    array,_ = freenect.sync_get_video()
    array = cv.cvtColor(array, cv.COLOR_RGB2BGR)
    return array

def get_depth():
    array,_ = freenect.sync_get_depth()
    array = array.astype(np.uint8)
    return array

if __name__ == '__main__':
    while 1:
        frame = get_video()
        depth = get_depth()
        cv.imshow('video', frame)
        cv.imshow('depth', depth)
        
        if cv.waitKey(1)  & 0xFF == ord('q'):
                break
            
    cv.destroyAllWindows()

