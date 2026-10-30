import numpy as np
import tensorflow as tf

from emitter_optimizer.engine import CollisionMap, DensityMap, MapType, Solver

MAP_SCALE = (10.0, 10.0)
GRID_SIZE = (8, 8)


def signal(distance: tf.Tensor) -> tf.Tensor:
    return tf.exp(-distance)


def sensor(received: tf.Tensor) -> tf.Tensor:
    return received


def make_solver(
    *,
    density_map: DensityMap | None = None,
    collision_map: CollisionMap | None = None,
    n_iteration: int = 15,
) -> Solver:
    return Solver(
        n_emitters=3,
        density_map=density_map,
        collision_map=collision_map,
        map_scale=MAP_SCALE,
        grid_size=GRID_SIZE,
        emitter_function=signal,
        sensor_function=sensor,
        n_iteration=n_iteration,
        epsilon=0.1,
    )


def test_training_maximizes_the_gain() -> None:
    solver = make_solver()
    before = solver.field.gain(solver.emitters_positions)

    positions, history = solver.train()

    assert float(solver.field.gain(positions)) > float(before)
    assert len(history) == solver.n_iteration


def test_a_density_map_weights_the_grid() -> None:
    density = np.ones((4, 4))
    density[0, :] = 0.0
    solver = make_solver(
        density_map=DensityMap.from_data(density, MapType.GRID, MapType.GRID)
    )

    values = solver.field.value_map(solver.emitters_positions)

    assert values.shape == GRID_SIZE
    assert float(tf.reduce_min(values)) >= 0.0


def test_a_segment_between_two_points_blocks_the_signal() -> None:
    obstacle = np.array([[[-1.0, -1.0], [1.0, 1.0]]])
    solver = make_solver(
        collision_map=CollisionMap.from_data(
            obstacle,
            MapType.SEGMENTS,
            MapType.SEGMENTS,
        )
    )

    blocked = solver.field.path_is_blocked(
        tf.constant([-1.0, 1.0]),
        tf.constant([1.0, -1.0]),
    )
    clear = solver.field.path_is_blocked(
        tf.constant([0.0, 0.0]),
        tf.constant([1.0, 0.0]),
    )

    assert bool(blocked)
    assert not bool(clear)


def test_solving_updates_the_positions_and_the_history() -> None:
    solver = make_solver(n_iteration=3)

    solver.solve()

    assert solver.history
    assert not solver.is_working
