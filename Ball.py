import numpy as np


class Ball(object):
    mass: np.float
    radius: np.float
    location: np.ndarray
    velocity: np.ndarray

    def __init__(self, location, velocity,radius,mass=1):
        self.location = location if location is np.ndarray else np.array(location)
        self.velocity = velocity if velocity is np.ndarray else np.array(velocity)
        self.radius = radius
        self.mass = mass

    def linear_propagate(self,time):
        self.location += self.velocity*time


class Ball_2D(Ball):
    pass


class Ball_3D():
    pass