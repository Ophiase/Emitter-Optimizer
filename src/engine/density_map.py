from .map_type import MapType

class DensityMap:
    def __init__(self, data, 
            data_format : MapType = MapType.GRID,
            storage_type : MapType = MapType.GRID,
            copy_constructor = False
            ):
        
        self.storage_type = storage_type
        self.data_format = data_format

        if (copy_constructor) :
            self.data = data
            return
        
        match(data_format, storage_type) :
            case MapType.GRID, MapType.GRID:
                self.data = data

            case _  :
                raise NotImplementedError()
    
    def copy(self):
        return DensityMap(self.data.copy(), 
                     self.data_format, 
                     self.storage_type, True)