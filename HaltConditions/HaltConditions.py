from .HaltConditionComposition import HaltCondition, Or_OfTwoHaltConditions
from SystemState import SystemState
from typing import Tuple, Optional
import numpy as np
from time import time as get_cur_time_in_seconds


class SingularHaLTCondition(HaltCondition):
    last_system_state: Optional[SystemState]

    def __init__(self):
        self.last_system_state = None

    def add_new_system_state(self, current_system_state):
        if self.last_system_state is None or self.last_system_state.time <= current_system_state.time:
            self.last_system_state = current_system_state


class NeverHalt(SingularHaLTCondition):
    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        return False, None


class HaltImmediately(SingularHaLTCondition):
    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        return True, self.last_system_state


class HaltAtGivenSimulationTime(SingularHaLTCondition):
    target_time: float

    def __init__(self, target_time):
        super().__init__()
        self.target_time = target_time

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        if current_system_state.time >= self.target_time:
            propagation_time = self.target_time - self.last_system_state.time
            new_system_state = self.last_system_state.propagate_by(propagation_time)
            return True, new_system_state
        self.add_new_system_state(current_system_state)
        return False, None


class HaltAtGivenUserTime(SingularHaLTCondition):
    target_time: float

    def __init__(self, target_time_in_seconds):
        super().__init__()
        self.target_time = get_cur_time_in_seconds() + target_time_in_seconds

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        if get_cur_time_in_seconds() >= self.target_time:
            return True, current_system_state
        return False, None


class HaltAtGivenNumOfSteps(SingularHaLTCondition):
    target_num_of_collisions: int

    def __init__(self, target_num_of_collisions):
        super().__init__()
        self.target_num_of_collisions = target_num_of_collisions

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        if self.target_num_of_collisions == current_system_state.total_num_of_steps:
            return True, current_system_state
        if self.target_num_of_collisions > current_system_state.total_num_of_steps:
            raise Exception("bug in code, can't find system state with correct total_num_of_steps. update_and_check of HaltAtGivenNumOfSteps was not called on every iteration")
        return False, None


class HaltAtBallExitsRectangle(Or_OfTwoHaltConditions):
    def __init__(self, p1, p2):
        condx = HaltAtBallExits1DRegion(min(p1[0], p2[0]), max(p1[0], p2[0]), 0)
        condy = HaltAtBallExits1DRegion(min(p1[1], p2[1]), max(p1[1], p2[1]), 1)
        super().__init__(condx, condy)


class HaltAtBallExits1DRegion(SingularHaLTCondition):
    min: float
    max: float
    coordinate_index: int

    def get_upcoming_collision_time(self, coor_vals, vel_vals):
        # TODO Account for radii
        t_collide_with_max = (self.max - coor_vals) / vel_vals
        t_collide_with_min = (self.min - coor_vals) / vel_vals

        time_collide = np.inf
        for i in range(len(coor_vals)):
            coor = coor_vals[i]
            vel = vel_vals[i]
            t1 = (self.max - coor) / vel
            t1 = np.inf if t1 < 0 else t1
            t2 = (self.min - coor) / vel
            t2 = np.inf if t2 < 0 else t2
            time_collide = min(time_collide, t1, t2)
        return time_collide

    def __init__(self, min, max, coordinate_index):
        super().__init__()
        self.min, self.max = min, max
        self.coordinate_index = coordinate_index

    def update_and_check(self, current_system_state: SystemState) -> Tuple[bool, Optional[SystemState]]:
        coor_vals = current_system_state.balls_location[:, self.coordinate_index]
        if np.any(coor_vals < self.min) or np.any(coor_vals > self.max):
            coor_vals = self.last_system_state.balls_location[:, self.coordinate_index]
            vel_vals = self.last_system_state.balls_velocity[:, self.coordinate_index]
            collision_time = self.get_upcoming_collision_time(coor_vals, vel_vals)
            new_state = self.last_system_state.propagate_by(collision_time)
            return True, new_state
        self.add_new_system_state(current_system_state)
        return False, None
