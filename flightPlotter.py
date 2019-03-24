


class FlightPlotter:
    
    def __init__(self):
        
        
        
        
    def plotFlight(self, pts):
        print("Points recorded: ", len(pts))
        usable_pts = deque(maxlen=64)
        for i in range(0, len(pts)):
            point = pts[i]
            # filter out any noisy/garbage depth data and estimate 
            if (point.z == 0) & (i > 0):
                point.z = usable_pts[i-1].z
                print("Estimated depth data for point as", point.z)
            else:
                print("Point ok")
            
                   
#            print("New point:", tuple_as_list)
            
            # Add the modified points to the points queue
            usable_pts.append(point)
                
        x_val = [p.x for p in usable_pts]
        y_val = [p.y for p in usable_pts]
        y_val.reverse()
        z_val = [p.z for p in usable_pts]
        
        #The first depth value tends to be zero/garbage, so lets estimate it
        z_val[0] = z_val[1] - (z_val[2] - z_val[1])
        
        self.ax.plot(x_val, y_val, z_val)
        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.set_zlabel("Z (meters)")
        self.ax.set_xlim(0, 640)
        self.ax.set_ylim(0, 480)
        self.ax.set_zlim(0, 3000)
        # Set initial viewing angle
        self.ax.view_init(-90, -90)
        plt.show()
        
        distance = max(x_val) - min(x_val)
        print("Distance:", distance)
        
    
        