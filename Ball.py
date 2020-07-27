import numpy as np
from typing import Tuple, Optional


class Ball(object):
    mass: np.float
    radius: np.float
    location: np.ndarray
    velocity: np.ndarray
    color: Tuple[np.float, np.float, np.float]
    angle: Optional[float]
    angular_vel: Optional[float]
    id: int

    # Static
    id_of_next_ball = 0

    def __init__(self, location, velocity, radius, mass=1, angular_vel=None, color=None):
        self.id = Ball.id_of_next_ball
        Ball.id_of_next_ball += 1
        self.location = location if location is np.ndarray else np.array(location, dtype=float)
        self.velocity = velocity if velocity is np.ndarray else np.array(velocity, dtype=float)
        self.radius = radius
        self.mass = mass
        self.color = color
        if type(angular_vel) == float:  # Update angle only if angular velocity is a scalar (2D balls)
            self.angle = 0
        else:
            self.angle = None
        self.angular_vel = angular_vel

    def linear_propagate(self, time):
        self.location += self.velocity * time
        if self.angle is not None:
            self.angle = self.angle + self.angular_vel * time
