from HaltConditionComposition import HaltCondition
from SystemState import SystemState
from typing import Tuple
import numpy as np
from time import time as get_cur_time_in_seconds


class HaltAtGivenSimulationTime(HaltCondition):
    target_time: float

    def __init__(self, target_time):
        self.target_time = target_time

    def update_and_check(self, current_system_state: SystemState):
        if current_system_state.time >= self.target_time:
            return True
        return False


class HaltAtGivenUserTime(HaltCondition):
    target_time: float

    def __init__(self, target_time_in_seconds):
        self.target_time = get_cur_time_in_seconds() + target_time_in_seconds

    def update_and_check(self, current_system_state: SystemState):
        if get_cur_time_in_seconds() >= self.target_time:
            return True
        return False


class HaltAtGivenNumOfSteps(HaltCondition):
    target_num_of_collisions:int

    def __init__(self,target_num_of_collisions):
        self.target_num_of_collisions = target_num_of_collisions
    def update_and_check(self, current_system_state: SystemState):
        if self.target_num_of_collisions >= current_system_state.total_num_of_steps:
            return True
        return False


class HaltAtBallExitsRectangle(HaltCondition):
    xmin: float
    xmax: float
    ymin: float
    ymax: float

    def __init__(self, p1, p2):
        self.xmin, self.xmax = min(p1[0], p2[0]), max(p1[0], p2[0])
        self.ymin, self.ymax = min(p1[1], p2[1]), max(p1[1], p2[1])

    def update_and_check(self, current_system_state: SystemState):
        x_vals = current_system_state.balls_location[:, 0]
        y_vals = current_system_state.balls_location[:, 1]
        if np.any(x_vals < self.xmin) or np.any(x_vals > self.xmax):
            return True
        if np.any(y_vals < self.ymin) or np.any(y_vals > self.ymax):
            return True
        return False
