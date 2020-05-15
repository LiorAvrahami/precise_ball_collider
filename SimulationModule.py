from Ball import Ball
import numpy as np
from BounderyConditions import CyclicBounderyConditions_2D, SlipperyBounceBounderyConditions_2D
from typing import Tuple, List, Callable,Union
import time as TimeModule
from BallCollitionCalculatior import calc_collision_time_between_balls, handle_ball_collision
from SystemState import SystemState
from HultCondition import HultCondition

class StateInSimulationModuleCalculation(object):
    first_ball_index : int
    second_ball_index : int
    next_possible_interupts : List[Tuple]

    get_tuple = lambda self: (self.first_ball_index, self.second_ball_index, self.next_possible_interupts)
    get_calculation_progress = lambda self,num_of_balls: self.first_ball_index/num_of_balls + (self.second_ball_index-self.first_ball_index)/((num_of_balls - self.first_ball_index + 1)*num_of_balls)
    def reset(self):
        self.first_ball_index = 0
        self.second_ball_index = 0
        self.next_possible_interupts = []

    def __init__(self):
        self.reset()


class SimulationModule(object):

    time: float
    total_num_of_steps: int
    boundery : SlipperyBounceBounderyConditions_2D
    balls_arr : List[Ball]
    halt_condition: HultCondition
    state_in_calculation: StateInSimulationModuleCalculation

    def __init__(self,boundery_conditions,balls_arr):
        self.boundery = boundery_conditions
        self.balls_arr = balls_arr
        self.time = 0
        self.total_num_of_steps = 0
        self.state_in_calculation = StateInSimulationModuleCalculation()
        self.halt_condition = None #TODO

    def calculate_next_ball_dynamics(self, simulation_time_timeout = np.inf, simulation_steps_timeout = np.inf, user_time_timeout__sec = np.inf) -> List[SystemState]:
        """
        :param simulation_time_timeout:
        :param simulation_steps_timeout:
        :param user_time_timeout__sec:
        :return:
        """
        start_time = TimeModule.time()
        if simulation_time_timeout == None and simulation_steps_timeout == None and user_time_timeout__sec == np.inf:
            raise Exception("No Hulting Condition Was Passed To \"calculate_next_ball_dynamics\"")
        simulation_steps_left = simulation_steps_timeout
        acummilated_system_states = []
        while self.time < simulation_time_timeout and simulation_steps_left > 0 and TimeModule.time() - start_time < user_time_timeout__sec:
            acummilated_system_states.append(self.calculate_next_collition_state())
        return acummilated_system_states

    def continue_calculation(self,simulation_time_timeout = np.inf, simulation_steps_timeout = np.inf, user_time_timeout__sec = np.inf) -> Tuple[List[SystemState],float]:
        """
        :param simulation_time_timeout:
        :param simulation_steps_timeout:
        :param user_time_timeout__sec:
        :return:
        """
        if not np.isfinite(simulation_time_timeout) and not np.isfinite(simulation_steps_timeout) and not np.isfinite(user_time_timeout__sec) and self.halt_condition == None:
            raise Exception("No Hulting Condition Was Passed To \"calculate_next_ball_dynamics\"")
        start_calculation_progress = self.state_in_calculation.get_calculation_progress(len(self.balls_arr))
        start_time = TimeModule.time()
        b_should_timeout = lambda: self.time >= simulation_time_timeout or self.total_num_of_steps >= simulation_steps_timeout or TimeModule.time() - start_time >= user_time_timeout__sec
        acummilated_system_states = []
        #run calculation until timeout condition is reached
        while not b_should_timeout():
            new_system_state = self.do_quanta_of_calculation()
            if new_system_state is not None:
                acummilated_system_states.append(new_system_state)
        return acummilated_system_states, len(acummilated_system_states) + (self.state_in_calculation.get_calculation_progress(len(self.balls_arr)) - start_calculation_progress)

    def do_quanta_of_calculation(self) -> Union[SystemState,None]:
        first_ball_index,second_ball_index,next_possible_interupts = self.state_in_calculation.get_tuple()
        if first_ball_index < len(self.balls_arr):
            first_ball = self.balls_arr[first_ball_index]
            if second_ball_index < len(self.balls_arr):
                #collition with other ball
                second_ball = self.balls_arr[second_ball_index]
                collision_time = calc_collision_time_between_balls(first_ball, second_ball)
                if collision_time != None and np.isfinite(collision_time):
                    next_possible_interupts.append((collision_time, len(next_possible_interupts), handle_ball_collision, (first_ball, second_ball)))

                #update second ball index
                self.state_in_calculation.second_ball_index += 1
                return
            else:
                # collition with walls:
                collision_time, wall_index = self.boundery.calc_collision_time_with_walls(first_ball)
                if collision_time != None and np.isfinite(collision_time):
                    next_possible_interupts.append((collision_time, len(next_possible_interupts), self.boundery.handle_wall_collision, (first_ball, wall_index)))

                # update first and second ball indexes
                self.state_in_calculation.first_ball_index += 1
                self.state_in_calculation.second_ball_index = self.state_in_calculation.first_ball_index + 1
                return
        else:
            # finished with collition checking, calculate physics of impact and propagate
            time_step_till_next_interupt, interupt_index, interupt_handler_function, handler_paramiters = min(next_possible_interupts)

            # propagate balls
            for ball in self.balls_arr:
                ball.linear_propagate(time_step_till_next_interupt)
            self.time += time_step_till_next_interupt
            self.total_num_of_steps += 1

            # handle couse of interupt (collition physics)
            if interupt_handler_function != None:
                interupt_handler_function(*handler_paramiters)

            # update first and second ball indexes
            self.state_in_calculation.reset()
            return SystemState.generate_from_balls_array(self.time, handler_paramiters, self.balls_arr)

    def calculate_next_collition_state(self) -> SystemState:
        next_possible_interupts = []
        for first_ball_index in range(len(self.balls_arr)):
            first_ball = self.balls_arr[first_ball_index]

            # collition with balls:
            for second_ball_index in range(first_ball_index + 1, len(self.balls_arr)):
                second_ball = self.balls_arr[second_ball_index]
                collision_time = calc_collision_time_between_balls(first_ball, second_ball)
                if collision_time != None and np.isfinite(collision_time):
                    next_possible_interupts.append((collision_time,len(next_possible_interupts), handle_ball_collision, (first_ball, second_ball)))

            # collition with walls:
            collision_time, wall_index = self.boundery.calc_collision_time_with_walls(first_ball)
            if collision_time != None and np.isfinite(collision_time):
                next_possible_interupts.append(
                    (collision_time,len(next_possible_interupts), self.boundery.handle_wall_collision, (first_ball, wall_index)))

        # next interupt is the one that happens first
        time_step_till_next_interupt,interupt_index , interupt_handler_function, handler_paramiters = min(next_possible_interupts)

        # propagate balls
        for ball in self.balls_arr:
            ball.linear_propagate(time_step_till_next_interupt)
        self.time += time_step_till_next_interupt
        self.total_num_of_steps += 1

        # handle couse of interupt (collition physics)
        if interupt_handler_function != None:
            interupt_handler_function(*handler_paramiters)
        return SystemState.generate_from_balls_array(self.time,handler_paramiters,self.balls_arr)

    def was_halt_condition_met(self) -> bool:
        return False #TODO
