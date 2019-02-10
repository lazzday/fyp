'''
Simple example of stereo image matching and point cloud generation.
Resulting .ply file cam be easily viewed using MeshLab ( http://meshlab.sourceforge.net/ )
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv
import imutils

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')


if __name__ == '__main__':
    print('loading images...')
#    imgL = cv.pyrDown(cv.imread('aloeL.jpg'))  # downscale images for faster processing
#    imgR = cv.pyrDown(cv.imread('aloeR.jpg'))
    
#    cams_test = 10
#    for i in range(0, cams_test):
#        cap = cv.VideoCapture(i)
#        test, frame = cap.read()
#        print("i : "+ str(i) + "/// result: " + str(test))
#        cap.release()
    
    left_capture = cv.VideoCapture(2)
    right_capture = cv.VideoCapture(3) 
    
    if (left_capture.isOpened() == False | left_capture.isOpened() == False):
        print("Error opening video stream")
    
    window_size = 3
    min_disp = 16
    num_disp = 112-min_disp
    stereo = cv.StereoSGBM_create(minDisparity = min_disp,
            numDisparities = num_disp,
            blockSize = 16,
            P1 = 8*3*window_size**2,
            P2 = 32*3*window_size**2,
            disp12MaxDiff = 1,
            uniquenessRatio = 10,
            speckleWindowSize = 100,
            speckleRange = 32
    )
    
    while (left_capture.isOpened() & right_capture.isOpened()):

        ret1, imgL = left_capture.read()
        ret2, imgR = right_capture.read()
            
        if(ret1 & ret2):
            
            imgL = cv.rotate(imgL, cv.ROTATE_90_CLOCKWISE)
            imgR = cv.rotate(imgR, cv.ROTATE_90_COUNTERCLOCKWISE)    
            
            cv.imshow('left', imgL)
            cv.imshow('right', imgR)
            
                   
#            ipy
            
            if cv.waitKey(1)  & 0xFF == ord('q'):
                break
        else:
            break
    #
#    # disparity range is tuned for 'aloe' image pair
#    
#    
#
##    print('computing disparity..#            imgR = imutils.rotate(imgR, 270)    .')
#    
#
##    print('generating 3d point cloud...',)
##    h, w = imgL.shape[:2]
##    f = 0.8*w                          # guess for focal length
##    Q = np.float32([[1, 0, 0, -0.5*w],
##                    [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
##                    [0, 0, 0,     -f], # so that y-axis looks up
##                    [0, 0, 1,      0]])
##    points = cv.reprojectImageTo3D(disp, Q)
##    colors = cv.cvtColor(imgL, cv.COLOR_BGR2RGB)
##    mask = disp > disp.min()
##    out_points = points[mask]
##    out_colors = colors[mask]
##    out_fn = 'out.ply'
##    write_ply('out.ply', out_points, out_colors)
##    print('%s saved' % 'out.ply')
#
    left_capture.release()
    right_capture.release()
    cv.destroyAllWindows()