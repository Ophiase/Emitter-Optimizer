import tensorflow as tf
import numpy as np
from typing import List, Tuple, Optional
import cv2

class Geometry :

    # LINEAR ALGEBRA

    @staticmethod
    @tf.function
    def interpolate(x : tf.Variable, y : tf.Variable, alpha : tf.Variable) -> tf.Variable:
        return x*alpha + y*(1-alpha)
    
    @staticmethod
    @tf.function
    def project_onto_grid(
            x: tf.Tensor, 
            world_shape: Tuple[tf.Tensor, tf.Tensor], 
            grid_shape: Tuple[tf.Tensor, tf.Tensor]
            ) -> List[tf.Tensor]:
        '''
        Convert world space to grid space.
        '''
        
        return [
            int(tf.floor(grid_shape[0] * x[0] / world_shape[0])),
            int(tf.floor(grid_shape[1] * x[1] / world_shape[1]))
        ]
    
    @staticmethod
    @tf.function
    def project_onto_world(
            x : Tuple[int, int], 
            world_shape : Tuple[float, float], 
            grid_shape : Tuple[int, int]
        ) -> Tuple[int, int] :
        '''
        Convert grid space to world space.
        '''
        
        return [
            world_shape[0] * x[0] / grid_shape[0],
            world_shape[1] * x[1] / grid_shape[1]
        ]
    
    @staticmethod
    @tf.function
    def project_onto_world_vect(
            positions : Tuple[int, int], 
            world_shape : Tuple[float, float], 
            grid_shape : Tuple[int, int]
        ) -> Tuple[int, int] :
        '''
        Convert grid space to world space.
        '''

        rx = world_shape[0] / grid_shape[0]
        ry = world_shape[1] / grid_shape[1]

        return tf.concat([
                positions[:, 0:1] * rx,
                positions[:, 1:2] * ry
            ], axis=-1)
    

    # INTERSECT

    @staticmethod
    @tf.function
    def intersect(
            segment_1 : Tuple[tf.Tensor], segment_2 : Tuple[tf.Tensor]
            ) -> tf.Tensor:
        '''
        Detect if segment_1 and segment_2 intersect.
        '''

        @tf.function
        def ccw(A: tf.Tensor, B: tf.Tensor, C: tf.Tensor) -> tf.Tensor:
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
        A, B = segment_1[0], segment_1[1] 
        C, D = segment_2[0], segment_2[1]

        return ( ccw(A,C,D) != ccw(B,C,D)) and (ccw(A,B,C) != ccw(A,B,D))

    @staticmethod
    @tf.function
    def there_is_an_obstacle_using_segments(
                x: tf.Tensor, y: tf.Tensor, 
                collision_segments: List[List[tf.Tensor]]
            ) -> tf.Tensor:
        '''
        Detect if there is an obstacle between x and y in collision_segments
        '''

        result = False
        for segment in collision_segments:
            if Geometry.intersect([x, y], segment) :
                result = True

        return result
    
    @staticmethod
    @tf.function
    def how_much_obstacle(x_grid : int, y_grid : int, collision_map : tf.Tensor, samples : int = 20):
        '''
        Obsolete function.
        '''
        acc = 1.0
        for i in range(samples):
            coord = Geometry.interpolate(x_grid, y_grid, i/samples)
            acc * collision_map[coord[0], coord[1]]
        return acc

    # GENERATE DATA

    @staticmethod
    def generate_points_from_density_map(density_map : Optional[np.ndarray], 
                                         output_scale : Tuple[float], n : int) -> tf.Variable:
        """
        Generate n points distributed according to the density map.

        Parameters:
        - density_map (numpy.ndarray or None): 2D array representing the density map.
        - output_scale (tuple): Tuple (u, v) representing the output scale.
        - n (int): Number of points to generate.

        Returns:
        - tf tensor: Array of generated points with shape (n, 2).
        """

        if density_map is None or np.all(density_map == 0):
            # Use a uniform distribution if density_map is None or consists only of zeros
            coordinates = np.random.uniform(size=(n, 2)) * np.array(output_scale)
        else:
            density_map = density_map.numpy()
            normalized_density = density_map / density_map.sum()

            flattened_density = normalized_density.flatten()
            indices = np.random.choice(flattened_density.size, size=n, p=flattened_density)
            coordinates = np.column_stack(np.unravel_index(indices, density_map.shape))

            coordinates = coordinates.astype(float) + 0.499
            coordinates = coordinates * (np.array(output_scale) / np.array(density_map.shape))
        
        coordinates[:, [0, 1]] = coordinates[:, [1, 0]]
        
        return tf.Variable(coordinates, dtype=tf.float32)
    
    @staticmethod
    def make_grid(grid_size, map_scale) -> tf.constant :
        T = tf.constant(
            [[
                (x, y) for x in range(grid_size[1])
            ] for y in range(grid_size[0]) ],
            dtype=tf.float32
        )

        reshaped_positions = tf.reshape(T, (-1, 2))
        mapped_values = Geometry.project_onto_world_vect(
            reshaped_positions, map_scale, grid_size)
        result = tf.reshape(tf.stack(mapped_values), T.shape)

        '''
        
        print(tf.shape(reshaped_positions))
        mapped_values = tf.vectorized_map(
            lambda x: Geometry.project_onto_world(x, map_scale, grid_size), 
            reshaped_positions)
        print(tf.shape(mapped_values))
             
        '''

        return result
    
    @staticmethod
    def adjust_map(image, size) -> tf.constant:
        image = cv2.resize(image, size)
        image = np.mean(image, axis=2)/255.0
        return tf.constant(image, dtype=tf.float32)