import numpy as np

class Utils:

    @staticmethod
    def getClosestPixelToCenter(valid_positions = [], center = (0, 0)):
        distance_average = lambda x, y: (x[0] - y[0])**2 + (x[1] - y[1])**2
        if len(valid_positions) > 0:
            return min(valid_positions, key=lambda co: distance_average(co, center)) 
        else:
            return center