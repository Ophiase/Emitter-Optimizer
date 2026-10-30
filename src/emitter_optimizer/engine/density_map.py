from dataclasses import dataclass

import numpy as np

from emitter_optimizer.engine.map_type import MapType


@dataclass(eq=False)
class DensityMap:
    """How much each point of the map is worth, stored as a grid of weights."""

    data: np.ndarray
    storage_type: MapType = MapType.GRID

    @classmethod
    def from_data(
        cls,
        data: np.ndarray,
        data_format: MapType,
        storage_type: MapType,
    ) -> DensityMap:
        if data_format is MapType.GRID and storage_type is MapType.GRID:
            return cls(data, storage_type)
        message = f"cannot read a {data_format} map as {storage_type}"
        raise NotImplementedError(message)
