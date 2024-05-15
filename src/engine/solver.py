import numpy as np
import tensorflow as tf

from .geometry import Geometry
from .map_type import MapType
from .density_map import DensityMap
from .collision_map import CollisionMap

from typing import Tuple, List, Optional, Callable
import matplotlib.pyplot as plt
import matplotlib

class Solver :
    def __init__(self, 
                n_emitters : int,
                density_map : Optional[DensityMap], 
                collision_map : Optional[CollisionMap],
                
                map_scale : Tuple[float], grid_size : Tuple[int],
                emitter_function, sensor_function,
                n_iteration : int, epsilon : float,

                update_callback : Optional[Callable] = None, 
                update_rate : int = 200
                ):
        
        def density_grid_decoding() :
            self.density_map.data = Geometry.adjust_map(
                self.density_map.data, grid_size)
            
            # We encode positions in map_scale to ensure validy of distance functions
            self.emitters_positions = Geometry.generate_points_from_density_map(
                self.density_map.data, 
                map_scale, n_emitters
                )

        self.density_map = None
        if density_map is None :
            self.emitters_positions = Geometry.generate_points_from_density_map(
                None, map_scale, n_emitters
            )
        else :
            self.density_map = density_map.copy()
            match (self.density_map.storage_type) :
                case MapType.GRID: density_grid_decoding()
                case _ : raise NotImplementedError()

        def denormalize_collision_map():
            new_segments = []
            for segment in self.collision_map.data:
                new_segments.append([
                    segment[0] * map_scale[0] ,
                    segment[1] * map_scale[1]
                ])

            self.collision_map.data = tf.constant(new_segments, dtype=tf.float32)
            
        self.collision_map = None if collision_map is None else collision_map.copy()
        if self.collision_map is not None :
            denormalize_collision_map()

        self.map_scale = map_scale
        
        self.grid_size = grid_size
        self.grid = Geometry.make_grid(grid_size, map_scale)
        
        self.emitter_function = emitter_function
        
        self.sensor_function = sensor_function
        
        self.n_iteration = n_iteration
        self.epsilon = epsilon


        if update_callback is None:
            self.update_callback = lambda x = None, history = None : x
        else :
            self.update_callback = update_callback

        self.update_callback()
        
        self.update_rate = update_rate

        # -----------------------------------

        self.is_working = False
        self.is_aborting = False
        self.history = []

        self.debug = False

    # -----------------------------------

    @tf.function
    def there_is_a_collision(self, emitter, position) :
        '''
            Check if there is a collision between 
            an emitter and a given position.
        '''
        if self.collision_map is None :
            return False

        match (self.collision_map.storage_type) :
            case MapType.SEGMENTS:
                return Geometry.there_is_an_obstacle_using_segments(
                    emitter, position, self.collision_map.data)
            case _ :
                raise NotImplementedError()

    @tf.function
    def sum_signals(self, position, emitter_positions) :
        '''
        Sum of signals received at a position.
        '''
        value_sum = 0.0
        for emitter in emitter_positions:
            if not self.there_is_a_collision(emitter, position) :            
                distance = tf.norm(emitter - position)
                value_sum += self.emitter_function(distance)
        return value_sum

    @tf.function
    def get_density(self, position) :
        if self.density_map is None : return 1.0
        match self.density_map.storage_type :
            case MapType.GRID :
                coord = Geometry.project_onto_grid(
                    position, self.map_scale, self.grid_size)
                return self.density_map.data[coord[1]][coord[0]]
            case _ : raise NotImplementedError()

    @tf.function
    def value_xy(self, position, emitter_positions):
        '''
        Valuation of a position : (sensor_function(sum_distances(u)) x density_map(u))
        '''
        aggregate = self.sum_signals(position, emitter_positions)
        value = self.sensor_function(aggregate)

        return value * self.get_density(position)

    @tf.function
    def vectorized_value_xy(self, emitter_positions):
        '''
        Map of valuation (for previsualisation)
        '''
        reshaped_positions = tf.reshape(self.grid, (-1, 2))
        mapped_values = tf.vectorized_map(lambda x: self.value_xy(x, emitter_positions), reshaped_positions)
        result = tf.reshape(mapped_values, tf.shape(self.grid)[:-1])
        
        return result

    @tf.function
    def gain(self, emitter_positions):
        '''
        Average gain over map.
        '''
        reshaped_positions = tf.reshape(self.grid, (-1, 2))
        mapped_values = tf.vectorized_map(
                lambda x: self.value_xy(x, emitter_positions), 
            reshaped_positions)
        
        return tf.reduce_sum(mapped_values) / (self.grid_size[0] * self.grid_size[1])

    # -----------------------------------

    def make_fig(self, x=None, figsize : Tuple[int] = (6, 4)):
        if x is None:
            x = self.emitters_positions
        
        value = self.vectorized_value_xy(x)
        value = value.numpy()
        fig, ax = plt.subplots(figsize=figsize)

        ax.scatter(
            x[:, 0], 
            x[:, 1])
        ax.set_xlim(0, self.map_scale[0])
        ax.set_ylim(self.map_scale[1], 0)

        ax.imshow(value,
                aspect='auto', origin='upper', 
                extent=(0, self.map_scale[0], self.map_scale[1], 0), 
        cmap='plasma', vmin=-1, vmax=1)
    

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Emitters positions")
        ax.grid(True)

        return fig

    # -----------------------------------

    def solve(self) -> None:
        if self.is_working : return

        self.is_working = True
        print("Solver is working ..")
        result = self.train()

        if result is None:
            self.is_working = False 
            self.is_aborting = False
            return
        
        x, history = result
        self.emitters_positions = x
        self.history = history

        self.is_working = False
        self.update_callback(x, self.history)
        print("Finished working")

    def abort(self) -> None:
        if self.is_aborting or not self.is_working : return
        print("Aborting ..")
        self.is_aborting = True

    def train(self) -> Optional[Tuple[tf.Variable, np.ndarray]]:
        x = tf.Variable(tf.identity(self.emitters_positions), trainable=True)
        
        history = self.history.copy()
        optimizer = tf.keras.optimizers.Nadam(learning_rate=self.epsilon)
        
        for i in range(self.n_iteration) :
            if self.is_aborting :
                self.is_aborting = False
                return x, history
            
            with tf.GradientTape() as tape:
                error = tf.constant(
                    -self.gain(x), 
                    dtype=tf.float32)
            
            gradients = tape.gradient(error, x)
            optimizer.apply_gradients([(gradients, x)])
            history.append(error.numpy())

            if i % self.update_rate == 0:
                self.update_callback(x, history)

        return x, history
    
    # -----------------------------------