
from .map_type import MapType

import matplotlib.pyplot as plt
import numpy as np
import cv2

import matplotlib

class CollisionMap:
    def __init__(self, data, 
            data_format : MapType = MapType.GRID,
            storage_type : MapType = MapType.SEGMENTS,
            copy_constructor = False
            ):
        
        self.storage_type = storage_type

        if copy_constructor :
            self.data = data.copy()
            return

        match(data_format, storage_type) :
            case MapType.GRID, MapType.SEGMENTS:
                self.data = self.grid_to_segment(data)
            case MapType.SEGMENTS, MapType.SEGMENTS:
                self.data = data
            case _  :
                raise NotImplementedError()
            
    def contour_to_edge_list(self, shape, map) :
        segments = []
        for i in range(shape.shape[0]):
            j = (i + 1) % shape.shape[0]

            last = shape[i][0]
            current = shape[j][0]

            segments.append([
                [last[0]    / map.shape[0], last[1]    / map.shape[0]],
                [current[0] / map.shape[0], current[1] / map.shape[1]]
            ])
        return segments
    
    def grid_to_segment(self, map):
        '''
            On init, transforms data as a map to data as segments.
        '''

        map = np.mean(map, axis=2)/255.0
        map_thresholded = cv2.Canny(np.uint8(map*255), 300, 300, 3)
        contour, _ = cv2.findContours(
            map_thresholded, cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE)

        segments = []
        for shape in contour:
            segments += self.contour_to_edge_list(shape, map)
            
        return np.array(segments)
    
    def copy(self):
        return CollisionMap(self.data, 
                            storage_type=self.storage_type, 
                            copy_constructor=True)