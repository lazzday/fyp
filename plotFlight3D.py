import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



class PlotFlight3D:
    
    def __init__(self):
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection = '3d')
        self.ax.plot3D(0, 0, 0, 'yellow')
        
        
    def plotPoint(self, x, y, z):
        self.ax.cla()
        self.ax.plot3D(z, y, z, 'yellow')