import abc
import numpy as np
from Ball import Ball
from typing import Tuple

class BounderyConditions(abc.ABC):
    @abc.abstractmethod
    def calc_collision_time_with_walls(self, ball: Ball) -> Tuple[float, int]:
        """
        :return: a tuple: (collision time, index of colliding wall) the "index of colliding wall" should be passed to "handle_wall_collision"
        """
        pass

    @abc.abstractmethod
    def handle_wall_collision(self,ball: Ball,wall_index: int):
        """
        :param wall_index: the wall_index of colliding wall, this value is returned from "calc_collision_time_with_walls"
        """
        pass

    @staticmethod
    def _calc_collision_time_with_wall_1d(ball_edge_x, wall_x, ball_vel_x):
        if ball_vel_x == 0:
            return np.inf
        ret = (wall_x - ball_edge_x) / ball_vel_x
        return ret if ret > 0 else np.inf

class RectangleBoundery_2D(BounderyConditions):
    wall_x_0 :float
    wall_x_1 :float
    wall_y_0 :float
    wall_y_1 :float

    #static Properties
    wall_x_0_key = "left"
    wall_x_1_key = "right"
    wall_y_0_key = "down"
    wall_y_1_key = "up"
    def __init__(self,wall_x_0 = -1, wall_x_1 = 1, wall_y_0 = -1, wall_y_1 = 1, ):
        self.wall_x_0 = wall_x_0
        self.wall_x_1 = wall_x_1
        self.wall_y_0 = wall_y_0
        self.wall_y_1 = wall_y_1

    def calc_collision_time_with_walls(self,ball: Ball) -> Tuple[float,int]:
        """
        :return: a tuple: (collision time, key of colliding wall) the tuple's contents should be passed in this order to "handle_wall_collision"
        """
        ret_1 = self._calc_collision_time_with_wall_1d (ball.location[0] - ball.radius,self.wall_x_0,ball.velocity[0]) , self.wall_x_0_key
        ret_2 = self._calc_collision_time_with_wall_1d (ball.location[0] + ball.radius,self.wall_x_1,ball.velocity[0]) , self.wall_x_1_key
        ret_3 = self._calc_collision_time_with_wall_1d (ball.location[1] - ball.radius,self.wall_y_0,ball.velocity[1]) , self.wall_y_0_key
        ret_4 = self._calc_collision_time_with_wall_1d (ball.location[1] + ball.radius,self.wall_y_1,ball.velocity[1]) , self.wall_y_1_key
        return min(ret_1,ret_2,ret_3,ret_4)

class CyclicBounderyConditions_2D(RectangleBoundery_2D):
    #TODO FIX BUG: balls need to collide with the part of this ball that passed throu the boundery (possible fix is to creat a new ball at the mirror position and remove current ball when it completly exits bounds)
    def handle_wall_collision(self, ball: Ball, wall_key: int):
        if wall_key == self.wall_x_0_key:
            ball.location[0] = self.wall_x_1
        if wall_key == self.wall_x_1_key:
            ball.location[0] = self.wall_x_0
        if wall_key == self.wall_y_0_key:
            ball.location[0] = self.wall_y_1
        if wall_key == self.wall_y_1_key:
            ball.location[0] = self.wall_y_0

class SlipperyBounceBounderyConditions_2D(RectangleBoundery_2D):
    def handle_wall_collision(self, ball: Ball, wall_key: int):
        if wall_key == self.wall_x_0_key or wall_key == self.wall_x_1_key:
            ball.velocity = ball.velocity*[-1,1]
        if wall_key == self.wall_y_0_key or wall_key == self.wall_y_1_key:
            ball.velocity = ball.velocity*[1,-1]