from Ball import Ball
import numpy as np
from BounderyConditions import CyclicBounderyConditions_2D, SlipperyBounceBounderyConditions_2D
from typing import Tuple, List, Callable, Union, Generator
import time as TimeModule
from BallCollitionCalculatior import calc_collision_time_between_balls, handle_ball_collision
from SystemState import SystemState
from HultCondition import HultCondition


# class StateInSimulationModuleCalculation(object):
#     first_ball_index: int
#     second_ball_index: int
#     next_possible_interupts: List[Tuple]
#
#     get_tuple = lambda self: (self.first_ball_index, self.second_ball_index, self.next_possible_interupts)
#     get_calculation_progress = lambda self, num_of_balls: self.first_ball_index / num_of_balls + (self.second_ball_index - self.first_ball_index) / (
#                 (num_of_balls - self.first_ball_index + 1) * num_of_balls)
#
#     def reset(self):
#         self.first_ball_index = 0
#         self.second_ball_index = 0
#         self.next_possible_interupts = []
#
#     def __init__(self):
#         self.reset()


class SimulationModule(object):
    time: float
    total_num_of_steps: int
    boundery: SlipperyBounceBounderyConditions_2D
    balls_arr: List[Ball]
    halt_condition: HultCondition
    simulation_propagation_generator: Generator[Tuple[List[SystemState], float], Callable[[None], bool],None]  # creatd by _get_simulation_propagation_generator at initialisation

    def __init__(self, boundery_conditions, balls_arr):
        self.boundery = boundery_conditions
        self.balls_arr = balls_arr
        self.time = 0
        self.total_num_of_steps = 0
        self.simulation_propagation_generator = self._get_simulation_propagation_generator()
        next(self.simulation_propagation_generator)
        self.halt_condition = None  # TODO

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
            # Todo: handle simulation ended
            pass

    def _get_simulation_propagation_generator(self) -> Generator[Tuple[List[SystemState], float], Callable[[None], bool],None]:
        """
        creates a generator that, when re-called, calculates the next simulation states until reaches timeout or the halt condition.
        returned generator documentation:
        yields - list of SystemState filled with the following simulation sates of the simulation.
        receives via send arg on recall - a function that indicates whether the current generator call should pause and yield accumulated data. (if timed out, the generator yields the accumulated states and waits for the next call)
        """
        b_should_pause_calculation = yield
        out_simulationstates_buffer = []

        def pause_and_yield(first_ball_index, second_ball_index):
            nonlocal b_should_pause_calculation,out_simulationstates_buffer
            b_should_pause_calculation = yield out_simulationstates_buffer, len(out_simulationstates_buffer) + self.get_calculation_progress(first_ball_index, second_ball_index)
            out_simulationstates_buffer = []

        while not self.was_halt_condition_met():
            while b_should_pause_calculation(): # check if should pause and yield before starting step, (helps keep calculation steps whole, and is essential for case where there is only one ball)
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
            out_simulationstates_buffer.append(SystemState.generate_from_balls_array(self.time, handler_paramiters, self.balls_arr))

    def was_halt_condition_met(self) -> bool:
        return False  # TODO

    def get_calculation_progress(self, first_ball_index, second_ball_index):
        num_of_balls = len(self.balls_arr)
        return first_ball_index / num_of_balls + (second_ball_index - first_ball_index) / ((num_of_balls - first_ball_index + 1) * num_of_balls)

    # def calculate_next_collition_state(self) -> SystemState:
    #     next_possible_interupts = []
    #     for first_ball_index in range(len(self.balls_arr)):
    #         first_ball = self.balls_arr[first_ball_index]
    #
    #         # collition with balls:
    #         for second_ball_index in range(first_ball_index + 1, len(self.balls_arr)):
    #             second_ball = self.balls_arr[second_ball_index]
    #             collision_time = calc_collision_time_between_balls(first_ball, second_ball)
    #             if collision_time != None and np.isfinite(collision_time):
    #                 next_possible_interupts.append((collision_time, len(next_possible_interupts), handle_ball_collision, (first_ball, second_ball)))
    #
    #         # collition with walls:
    #         collision_time, wall_index = self.boundery.calc_collision_time_with_walls(first_ball)
    #         if collision_time != None and np.isfinite(collision_time):
    #             next_possible_interupts.append(
    #                 (collision_time, len(next_possible_interupts), self.boundery.handle_wall_collision, (first_ball, wall_index)))
    #
    #     # next interupt is the one that happens first
    #     time_step_till_next_interupt, interupt_index, interupt_handler_function, handler_paramiters = min(next_possible_interupts)
    #
    #     # propagate balls
    #     for ball in self.balls_arr:
    #         ball.linear_propagate(time_step_till_next_interupt)
    #     self.time += time_step_till_next_interupt
    #     self.total_num_of_steps += 1
    #
    #     # handle couse of interupt (collition physics)
    #     if interupt_handler_function != None:
    #         interupt_handler_function(*handler_paramiters)
    #     return SystemState.generate_from_balls_array(self.time, handler_paramiters, self.balls_arr)
    #
    # def continue_calculation(self, simulation_time_timeout=np.inf, simulation_steps_timeout=np.inf, user_time_timeout__sec=np.inf) -> Tuple[List[SystemState], float]:
    #     """
    #     :param simulation_time_timeout:
    #     :param simulation_steps_timeout:
    #     :param user_time_timeout__sec:
    #     :return:
    #     """
    #     if not np.isfinite(simulation_time_timeout) and not np.isfinite(simulation_steps_timeout) and not np.isfinite(user_time_timeout__sec) and self.halt_condition == None:
    #         raise Exception("No Hulting Condition Was Passed To \"calculate_next_ball_dynamics\"")
    #     start_calculation_progress = self.state_in_calculation.get_calculation_progress(len(self.balls_arr))
    #     start_time = TimeModule.time()
    #     b_should_timeout = lambda: self.time >= simulation_time_timeout or self.total_num_of_steps >= simulation_steps_timeout or TimeModule.time() - start_time >= user_time_timeout__sec
    #     acummilated_system_states = []
    #     # run calculation until timeout condition is reached
    #     while not b_should_timeout():
    #         new_system_state = self.do_quanta_of_calculation()
    #         if new_system_state is not None:
    #             acummilated_system_states.append(new_system_state)
    #     return acummilated_system_states, len(acummilated_system_states) + (self.state_in_calculation.get_calculation_progress(len(self.balls_arr)) - start_calculation_progress)
    #
    # def do_quanta_of_calculation(self) -> Union[SystemState, None]:
    #     first_ball_index, second_ball_index, next_possible_interupts = self.state_in_calculation.get_tuple()
    #     if first_ball_index < len(self.balls_arr):
    #         first_ball = self.balls_arr[first_ball_index]
    #         if second_ball_index < len(self.balls_arr):
    #             # collition with other ball
    #             second_ball = self.balls_arr[second_ball_index]
    #             collision_time = calc_collision_time_between_balls(first_ball, second_ball)
    #             if collision_time != None and np.isfinite(collision_time):
    #                 next_possible_interupts.append((collision_time, len(next_possible_interupts), handle_ball_collision, (first_ball, second_ball)))
    #
    #             # update second ball index
    #             self.state_in_calculation.second_ball_index += 1
    #             return
    #         else:
    #             # collition with walls:
    #             collision_time, wall_index = self.boundery.calc_collision_time_with_walls(first_ball)
    #             if collision_time != None and np.isfinite(collision_time):
    #                 next_possible_interupts.append((collision_time, len(next_possible_interupts), self.boundery.handle_wall_collision, (first_ball, wall_index)))
    #
    #             # update first and second ball indexes
    #             self.state_in_calculation.first_ball_index += 1
    #             self.state_in_calculation.second_ball_index = self.state_in_calculation.first_ball_index + 1
    #             return
    #     else:
    #         # finished with collition checking, calculate physics of impact and propagate
    #         time_step_till_next_interupt, interupt_index, interupt_handler_function, handler_paramiters = min(next_possible_interupts)
    #
    #         # propagate balls
    #         for ball in self.balls_arr:
    #             ball.linear_propagate(time_step_till_next_interupt)
    #         self.time += time_step_till_next_interupt
    #         self.total_num_of_steps += 1
    #
    #         # handle couse of interupt (collition physics)
    #         if interupt_handler_function != None:
    #             interupt_handler_function(*handler_paramiters)
    #
    #         # update first and second ball indexes
    #         self.state_in_calculation.reset()
    #         return SystemState.generate_from_balls_array(self.time, handler_paramiters, self.balls_arr)
