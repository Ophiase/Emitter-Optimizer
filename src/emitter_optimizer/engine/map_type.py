from enum import StrEnum


class MapType(StrEnum):
    """How a map is stored: as a grid of values or as a set of segments."""

    GRID = "grid"
    SEGMENTS = "segments"

    @classmethod
    def from_string(cls, text: str) -> MapType:
        match text.strip().upper():
            case "GRID":
                return cls.GRID
            case "SEGMENT" | "SEGMENTS":
                return cls.SEGMENTS
            case _:
                message = f"unknown map type: {text}"
                raise ValueError(message)
