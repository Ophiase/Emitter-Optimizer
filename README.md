# Emitter Optimizer
Find the optimal emitters positions on a map using user defined emitter.


## Table of Contents
- Introduction
    - [Model](#model)
    - [Demo](#demo)
- Functionality
    - [Features](#features)
- Setup
    - [Installation](#installation)
    - [Run](#run)
- Future Development
    - [Future Development](#future-development)

## Introduction
### Model
---

Optimizing signal coverage with emitters on a map involves maximizing a function $\mathcal G$ over emitter positions $U$, defined as follows:

- Emitter function $\varphi : \mathbb{R}^+ \to \mathbb{R}$ 
    - Takes the distance from the emitter as a parameter and returns the amount of signal perceived at this distance.
- Sensor function $\psi : \mathbb{R} \to \mathbb{R}$
    - Takes the sum of signals received at a given position and returns a score for the sensor.  
- $U$: the positions of emitters.
- Parameters $P := (E, \mu, C)$
    - $E$: A square map.
    - $\mu$: a density measure over $E$.
    - $C$: a list of segments that block the signal.
- $pass_C : (x, y) \to 1 - \prod_{s \in C} (1 - \mathbb{1}_{[x; y] \cap s})$
    - Returns 0 if the segment $[x; y]$ collides with a segment inside $C$, 1 otherwise.
- $dist : (x, y) \to || x - y ||_2$ 
- Received signal $r_{U, C} : x \to \sum_{y \in U}\varphi \big( dist(x, y) \big) \cdot pass_C(x, y)$
- Gain function $\mathcal G_P : U \to \int_E \psi \circ r_{U, C}(x) \, d\mu(x)$


### Demo
---
You can try to optimize emitters using the following density map and colliders map.
- ![](https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/map/value_001.png) : ``resources/map/value_001.png``
- ![](https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/map/collide_001.png) : ``resources/map/collide_001.png``
    - Image $\to$ segments might make too much segments. \
    Use the approximation ``resources/map/collide_001.numpy``
    - Note that solving wihout using colliders might be sufficient.

- ### Adjust the parameters
    - <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/interface_002.png" width=500>
    - For instance, you can modify the sensor/emitter function
        - <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/user_defined_sensor.png" width=300> <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/user_defined_emitter.png" width=300>
- ### Update the parameters and start the solver
    - Before/After solving. : </br> <img src=https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/render_000.png width=300> <img src=/resources/demo/render_199.png width=300>


## Setup
### Installation
- automatic install of dependencies :
```sh
./install_dependencies
```
- manual install of the dependencies :
```sh
pip install numpy tensorflow dearpygui
```
- condas install of the dependencies :
```sh
conda env create -f environment.yml
```

### Run
```sh
./run # first method
python3 src/main.py # second method
```

## Features
- Basic simulation : Gradient climbing of the gain function $\mathcal G$

- User defined emitter function $\varphi$
- User defined sensors activation function $\psi$
- User defined density map $\mu$
- User defined collision map $C$
    - As a grayscale map (that will be converted to segment)
    - As a numpy array of relatives positions.
- Save emitters positions

## Future Development
- Features
    - Optional optimizer (After multiples tests, we currently use Nadam by default)
        - <img src="https://raw.githubusercontent.com/Ophiase/Emitter-Optimizer/main/resources/demo/optimizer.png" width=300>
    - Finding the optimal number of sensors
- Misc
    - For a large number of emitters on a high-dimensional map, we can consider the following approximations of $\mathcal G$.
        - Almost every function used in the loss function can be approximated by a piecewise linear function $l$ on a relevant finite interval.
            - $f \approx l: x \to \sum_{J \in I} (\alpha_i x + \beta_i) \times \mathbb{1}_J(x)$
                - Where $I$ is a partition of $\mathbb{R}^n$ such that every $J$ is a polytope.
        - The Euclidean distance isn't a good candidate for piecewise linear function approximation, so it should be correctly approximated by Heron's method.
        - This implies that the loss function can be approximated by the integral of a piecewise linear function, which can be very fast to calculate using parallelization.
            - $||x, y||_2$ can be approximated using Heron's method.
            - $\varphi \approx l_1$, a piecewise linear function.
            - $\psi \approx l_2$, a piecewise linear function.
            - $\mu \approx \int l_3 \, d\lambda_2$, where $\lambda_2$ is Lebesgue's measure over $\mathbb{R}^2$.
            - $\mathcal{G}_P \approx \int_E l_1 \circ (\sum_y l_2(\text{dist}(\cdot, y)) \times \text{pass}_C(\cdot, y)) \, l_3 \, d\lambda_2$.
    - Manifold distance.
        - If the map $E$ is a chart over a manifold, we might want to use the distance over the manifold surface.
        - Example :
            - If we want to place emitters over Earth's continents. Our grid will be a chart  over the manifold $S^2$ and the distance will not be the euclidean distance.
    - Use a "compilation" optimizer for Python.