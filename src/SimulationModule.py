from .Ball import Ball
import numpy as np
from .BounderyConditions import CyclicBounderyConditions_2D, SlipperyBounceBounderyConditions_2D,BounderyConditions
from typing import Tuple, List, Callable, Union, Generator
import time as TimeModule
from .BallCollitionCalculatior import calc_collision_time_between_balls, handle_ball_collision
from .SystemState import SystemState
from .HaltConditions import HaltCondition
from src import HaltConditions
import pickle

class SimulationModule(object):
    _SimulationPropagationGeneratorType = Generator[Tuple[List[SystemState], float], Callable[[None], bool], Tuple[List[SystemState], float]]

    time: float
    total_num_of_steps: int
    boundery: BounderyConditions
    balls_arr: List[Ball]
    _halt_condition: HaltCondition
    simulation_propagation_generator: _SimulationPropagationGeneratorType  # creatd by _get_simulation_propagation_generator at initialisation
    b_end_of_simulation_reached: bool
    _b_force_stop:bool

    @property
    def halt_condition(self):
        return self._halt_condition

    @halt_condition.setter
    def halt_condition(self, val):
        self._halt_condition = val
        self._halt_condition.add_new_system_state(SystemState.generate_from_simulation_module(self, None))
        if self.b_end_of_simulation_reached:
            self.b_end_of_simulation_reached = False
            self.simulation_propagation_generator = self.get_simulation_propagation_generator()

    def __init__(self, balls_arr, boundery_conditions=None, halt_condition=None):
        self.boundery = boundery_conditions or SlipperyBounceBounderyConditions_2D()
        self.balls_arr = balls_arr
        self.time = 0
        self.total_num_of_steps = 0
        self.b_end_of_simulation_reached = False
        self.halt_condition = halt_condition or HaltConditions.NeverHalt()  # Must Come After Initialisation Of balls_arr,time,total_num_of_steps
        self.simulation_propagation_generator = self.get_simulation_propagation_generator()
        self._b_force_stop= False

    def update_from_system_state(self, system_state: SystemState):
        self.time = system_state.time
        self.total_num_of_steps = system_state.total_num_of_steps
        for i, ball in enumerate(self.balls_arr):
            ball.location = system_state.balls_location[i]
            ball.velocity = system_state.balls_velocity[i]
            ball.angle = system_state.balls_angle[i]
            ball.angular_vel = system_state.balls_angular_velocity[i]
            assert ball.id == system_state.balls_id[i]

    def calculate_next_ball_dynamics(self, simulation_time_timeout=np.inf, simulation_steps_timeout=np.inf, user_time_timeout__sec=np.inf) -> Tuple[List[SystemState], float]:
        """
        :param simulation_time_timeout:
        :param simulation_steps_timeout:
        :param user_time_timeout__sec:
        :return:
        """
        target_user_time = TimeModule.time() + user_time_timeout__sec
        target_num_of_steps = self.total_num_of_steps + simulation_steps_timeout
        b_should_pause_calculation = lambda: self.time >= simulation_time_timeout or self.total_num_of_steps >= target_num_of_steps or TimeModule.time() >= target_user_time
        try:
            return self.simulation_propagation_generator.send(b_should_pause_calculation)
        except StopIteration as ret:
            self.b_end_of_simulation_reached = True

            return ret.value

    def get_simulation_propagation_generator(self) -> _SimulationPropagationGeneratorType:
        propagation_generator = self._get_simulation_propagation_generator()
        next(propagation_generator)
        return propagation_generator

    def _get_simulation_propagation_generator(self) -> _SimulationPropagationGeneratorType:
        """
        creates a generator that, when re-called, calculates the next simulation states until reaches timeout or the halt condition.
        returned generator documentation:
        yields - list of SystemState filled with the following simulation sates of the simulation.
        receives via send arg on recall - a function that indicates whether the current generator call should pause and yield accumulated data. (if timed out, the generator yields the accumulated states and waits for the next call)
        """
        out_simulationstates_buffer = []

        def pause_and_yield(first_ball_index, second_ball_index):
            nonlocal b_should_pause_calculation, out_simulationstates_buffer
            b_should_pause_calculation = yield out_simulationstates_buffer, len(out_simulationstates_buffer) + self.get_calculation_progress(first_ball_index, second_ball_index)
            out_simulationstates_buffer = []

        b_should_pause_calculation = yield
        while True:
            while b_should_pause_calculation():  # check if should pause and yield before starting step, (helps keep calculation steps whole, and is essential for case where there is only one ball)
                yield from pause_and_yield(0, 0)

            next_possible_interupts = []
            for first_ball_index in range(len(self.balls_arr)):
                first_ball = self.balls_arr[first_ball_index]

                # collition with balls:
                for second_ball_index in range(first_ball_index + 1, len(self.balls_arr)):
                    while b_should_pause_calculation():  # check if should pause and yield before every pair calculation
                        yield from pause_and_yield(first_ball_index, second_ball_index)

                    second_ball = self.balls_arr[second_ball_index]
                    collision_time = calc_collision_time_between_balls(first_ball, second_ball)
                    if collision_time != None and np.isfinite(collision_time):
                        next_possible_interupts.append((collision_time, len(next_possible_interupts), handle_ball_collision, (first_ball, second_ball)))

                # collition with walls:
                collision_time, wall_index = self.boundery.calc_collision_time_with_walls(first_ball)
                if collision_time != None and np.isfinite(collision_time):
                    next_possible_interupts.append(
                        (collision_time, len(next_possible_interupts), self.boundery.handle_wall_collision, (first_ball, wall_index)))

            # next interupt is the one that happens first
            time_step_till_next_interupt, interupt_index, interupt_handler_function, handler_paramiters = min(next_possible_interupts)

            # propagate balls
            for ball in self.balls_arr:
                ball.linear_propagate(time_step_till_next_interupt)
            self.time += time_step_till_next_interupt
            self.total_num_of_steps += 1

            # handle couse of interupt (collition physics)
            if interupt_handler_function != None:
                interupt_handler_function(*handler_paramiters)
            out_simulationstates_buffer.append(SystemState.generate_from_simulation_module(self, handler_paramiters))

            # check halt condition
            b_halt_condition_met, final_system_state = self.halt_condition.update_and_check(out_simulationstates_buffer[-1])
            if b_halt_condition_met or self._b_force_stop:
                _b_force_stop = False
                if final_system_state is not None:
                    self.update_from_system_state(final_system_state)
                    out_simulationstates_buffer[-1] = final_system_state
                break

        return out_simulationstates_buffer, len(out_simulationstates_buffer)

    def get_calculation_progress(self, first_ball_index, second_ball_index):
        num_of_balls = len(self.balls_arr)
        return first_ball_index / num_of_balls + (second_ball_index - first_ball_index) / ((num_of_balls - first_ball_index + 1) * num_of_balls)

    def draw_current_situation(self):
        SystemState.generate_from_simulation_module(self, None).draw_state(self.boundery)

    def force_stop(self):
        self._b_force_stop = True

    def save_to_pickle(self,path_without_suffix):
        path = path_without_suffix + "_Simulation_Definition"
        new_sim = SimulationModule(self.balls_arr, self.boundery, self.halt_condition)
        new_sim.time = self.time
        new_sim.total_num_of_steps = self.total_num_of_steps
        new_sim.b_end_of_simulation_reached = self.b_end_of_simulation_reached
        new_sim.simulation_propagation_generator = None
        del new_sim.simulation_propagation_generator

        with open(path,"wb+") as f:
            pickle.dump(new_sim,f)

    @staticmethod
    def load_from_pickle(path_without_suffix):
        path = path_without_suffix + "_Simulation_Definition"
        with open(path, "rb") as f:
            new_sim = pickle.load(f)
        return new_sim

