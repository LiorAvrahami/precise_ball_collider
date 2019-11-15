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
    def _calc_collision_time_with_wall_1d(ball_x,wall_x,ball_vel_x):
        ret = (wall_x-ball_x)/ball_vel_x
        return ret if ret > 0 else np.inf

class RectangleBoundery_2D(BounderyConditions):
    wall_x_0 :float
    wall_x_1 :float
    wall_y_0 :float
    wall_y_1 :float

    #static Properties
    wall_x_0_index = 0
    wall_x_1_index = 1
    wall_y_0_index = 2
    wall_y_1_index = 3
    def __init__(self,wall_x_0 = -1, wall_x_1 = 1, wall_y_0 = -1, wall_y_1 = 1, ):
        self.wall_x_0 = wall_x_0
        self.wall_x_1 = wall_x_1
        self.wall_y_0 = wall_y_0
        self.wall_y_1 = wall_y_1

    def calc_collision_time_with_walls(self,ball: Ball) -> Tuple[float,int]:
        """
        :return: a tuple: (collision time, index of colliding wall) the tuple's contents should be passed in this order to "handle_wall_collision"
        """
        ret_1 = self._calc_collision_time_with_wall_1d(ball.location[0],self.wall_x_0,ball.velocity[0]) , self.wall_x_0_index
        ret_2 = self._calc_collision_time_with_wall_1d(ball.location[0],self.wall_x_1,ball.velocity[0]) , self.wall_x_1_index
        ret_3 = self._calc_collision_time_with_wall_1d(ball.location[1],self.wall_y_0,ball.velocity[1]) , self.wall_y_0_index
        ret_4 = self._calc_collision_time_with_wall_1d(ball.location[1],self.wall_y_1,ball.velocity[1]) , self.wall_y_1_index
        return min(ret_1,ret_2,ret_3,ret_4)

class CyclicBounderyConditions_2D(RectangleBoundery_2D):
    def handle_wall_collision(self, ball: Ball, wall_index: int):
        if wall_index == self.wall_x_0_index:
            ball.location[0] = self.wall_x_1
        if wall_index == self.wall_x_1_index:
            ball.location[0] = self.wall_x_0
        if wall_index == self.wall_y_0_index:
            ball.location[0] = self.wall_y_1
        if wall_index == self.wall_y_1_index:
            ball.location[0] = self.wall_y_0

