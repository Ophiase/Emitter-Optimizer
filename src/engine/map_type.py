from enum import Enum

'''
    Storage representation of map data
'''
class MapType(Enum):
    GRID = 0,
    SEGMENTS = 1
    FUNCTION = 2

    @classmethod
    def from_string(cls, map_type_str):
        match (map_type_str.upper()):
            case 'GRID': return cls.GRID
            case 'SEGMENT' | 'SEGMENTS': return cls.SEGMENTS
            case 'FUNCTION': return cls.FUNCTION
            case _ :
                return ValueError("Invalid MapType string {}".format(map_type_str))