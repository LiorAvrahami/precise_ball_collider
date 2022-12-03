import abc
import numpy as np
from .Ball import Ball
from typing import Tuple, Callable


class BounderyConditions(abc.ABC):
    on_wall_collision_event: Callable

    def __init__(self, on_wall_collision_event: Callable):
        """
        on_wall_collision_event: gets (ball,wall_index)
        """
        self.on_wall_collision_event = on_wall_collision_event

    @abc.abstractmethod
    def calc_collision_time_with_walls(self, ball: Ball) -> Tuple[float, object]:
        """
        :return: a tuple: (collision time, index of colliding wall) the "index of colliding wall" should be passed to "handle_wall_collision"
        """
        pass

    @abc.abstractmethod
    def handle_wall_collision(self, ball: Ball, wall_index: object):
        """
        :param wall_index: the wall_index of colliding wall, this value is returned from "calc_collision_time_with_walls"
        """
        if callable(self.on_wall_collision_event):
            self.on_wall_collision_event(ball=ball, wall_index=wall_index)

    @staticmethod
    def _calc_collision_time_with_wall_1d(ball_edge_x, wall_x, ball_vel_x) -> float:
        if ball_vel_x == 0:
            return np.inf
        ret = (wall_x - ball_edge_x) / ball_vel_x
        return ret if ret >= 0 else np.inf

    @property
    @abc.abstractmethod
    def x_limits(self):
        pass

    @property
    @abc.abstractmethod
    def y_limits(self):
        pass

    def draw(self, axes):
        pass


class RectangleBoundery_2D(BounderyConditions):
    wall_x_0: float
    wall_x_1: float
    wall_y_0: float
    wall_y_1: float

    # static Properties
    wall_x_0_key = "left"
    wall_x_1_key = "right"
    wall_y_0_key = "down"
    wall_y_1_key = "up"
    wall_x_keys = (wall_x_0_key, wall_x_1_key)
    wall_y_keys = (wall_y_0_key, wall_y_1_key)

    def __init__(self, wall_x_0=-1, wall_x_1=1, wall_y_0=-1, wall_y_1=1, on_wall_collision_event=None):
        super().__init__(on_wall_collision_event)
        self.wall_x_0 = wall_x_0
        self.wall_x_1 = wall_x_1
        self.wall_y_0 = wall_y_0
        self.wall_y_1 = wall_y_1

    def __repr__(self):
        return "{}:[x={:.5g},{:.5g}],[y={:.5g},{:.5g}]".format(type(self), self.wall_x_0, self.wall_x_1, self.wall_y_0, self.wall_y_1)

    def calc_collision_time_with_walls(self, ball: Ball) -> Tuple[float, object]:
        """
        :return: a tuple: (collision time, key of colliding wall) the tuple's contents should be passed in this order to "handle_wall_collision"
        """
        ret_1 = self._calc_collision_time_with_wall_1d(ball.location[0] - ball.radius, self.wall_x_0, ball.velocity[0]) if ball.velocity[0] < 0 else float(
            "infinity"), self.wall_x_0_key
        ret_2 = self._calc_collision_time_with_wall_1d(ball.location[0] + ball.radius, self.wall_x_1, ball.velocity[0]) if ball.velocity[0] > 0 else float(
            "infinity"), self.wall_x_1_key
        ret_3 = self._calc_collision_time_with_wall_1d(ball.location[1] - ball.radius, self.wall_y_0, ball.velocity[1]) if ball.velocity[1] < 0 else float(
            "infinity"), self.wall_y_0_key
        ret_4 = self._calc_collision_time_with_wall_1d(ball.location[1] + ball.radius, self.wall_y_1, ball.velocity[1]) if ball.velocity[1] > 0 else float(
            "infinity"), self.wall_y_1_key
        return min(ret_1, ret_2, ret_3, ret_4)

    @property
    def x_limits(self):
        return self.wall_x_0, self.wall_x_1

    @property
    def y_limits(self):
        return self.wall_y_0, self.wall_y_1

    def draw(self, axes):
        from matplotlib.patches import Rectangle
        axes.add_patch(Rectangle((self.wall_x_0, self.wall_y_0), self.wall_x_1 - self.wall_x_0, self.wall_y_1 - self.wall_y_0,
                                 alpha=1, facecolor='none', edgecolor="r"))


class CyclicBounderyConditions_2D(RectangleBoundery_2D):
    # TODO FIX BUG: balls need to collide with the part of this ball that passed throu the boundery (possible fix is to creat a new ball at the mirror position and remove current ball when it completly exits bounds)
    def handle_wall_collision(self, ball: Ball, wall_key: object):
        if wall_key == self.wall_x_0_key:
            ball.location[0] = self.wall_x_1
        if wall_key == self.wall_x_1_key:
            ball.location[0] = self.wall_x_0
        if wall_key == self.wall_y_0_key:
            ball.location[0] = self.wall_y_1
        if wall_key == self.wall_y_1_key:
            ball.location[0] = self.wall_y_0
        super().handle_wall_collision(ball, wall_key)


class SlipperyBounceBounderyConditions_2D(RectangleBoundery_2D):
    def handle_wall_collision(self, ball: Ball, wall_key: object):
        if wall_key == self.wall_x_0_key or wall_key == self.wall_x_1_key:
            ball.velocity = ball.velocity * [-1, 1]
        if wall_key == self.wall_y_0_key or wall_key == self.wall_y_1_key:
            ball.velocity = ball.velocity * [1, -1]
        super().handle_wall_collision(ball, wall_key)
