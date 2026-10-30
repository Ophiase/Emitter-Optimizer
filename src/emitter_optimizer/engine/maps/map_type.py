from enum import StrEnum


class MapType(StrEnum):
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
