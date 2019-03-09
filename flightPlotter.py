import matplotlib.pyplot as plt
from collections import deque


class FlightPlotter:
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection = '3d')
        
        
        
    def plotFlight(self, pts):
        print("Points recorded: ", len(pts))
        usable_pts = deque(maxlen=64)
        for i in range(0, len(pts)):
            # convert tuple to list and store in new queue of points (as lists)
            tuple_as_list = list(pts[i])
            print("Checking point", tuple_as_list)
            # filter out any noisy/garbage depth data and estimate 
            if (tuple_as_list[2] == 0) & (i > 1):
                tuple_as_list[2] = usable_pts[i-1][2]
                print("Estimated depth data for point as", tuple_as_list[2])
            else:
                print("Point ok")
            usable_pts.append(tuple_as_list)
                
        x_val = [x[0] for x in usable_pts]
        y_val = [x[1] for x in usable_pts]
        y_val.reverse()
        z_val = [x[2] for x in usable_pts]
        
        #The first depth value tends to be zero/garbage, so lets estimate it
        z_val[0] = z_val[1] - (z_val[2] - z_val[1])
        
        self.ax.plot(x_val, y_val, z_val)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_xlim(0, 640)
        self.ax.set_ylim(0, 480)
        self.ax.set_zlim(0, 3000)
        # Set initial viewing angle
        self.ax.view_init(-90, -90)
        plt.show()
        