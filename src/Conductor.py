import abc
import enum
import threading
import os
import numpy as np

from .SimulationModule import SimulationModule
from src import HaltConditions
from . import StatesToFileWritingModule
from time import time, sleep
import datetime
from typing import List, Generator
from .DrawingModule.simulation_animator import SimulationAnimator, FrameUpdate, ToFileSimulationAnimationSaver


class Conductor(abc.ABC):
    simulation_module: SimulationModule
    log_file_fullname: str
    b_write_log_data_to_screen: bool

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None):
        self.simulation_module = simulation_module
        self.log_file_fullname = log_file_fullname
        self.b_write_log_data_to_screen = True

    def log_txt(self, txt):
        if self.log_file_fullname is not None:
            with open(self.log_file_fullname, mode="a+") as f:
                f.write(txt)
        if self.b_write_log_data_to_screen:
            print(txt)

    def log_that_run_started(self):
        self.log_txt("run started")

    def log_that_run_ended(self):
        self.log_txt("run ended")

    def log_that_wrote_to_files(self, file_short_names: List[str]):
        self.log_txt("wrote to" + str(file_short_names))

    def log_that_Error_occured(self, error_object: Exception):
        self.log_txt("error occured\\nerror type: " +
                     str(type(error_object)) + "\\nerror messege" + str(error_object))

    def log_eta(self, total_work, work_done, time_elapsed):
        if work_done == 0:
            self.log_txt(f"estimated time left is: unknown\neta is: unknown")
            return
        work_completion_rate = work_done / time_elapsed
        work_left = total_work - work_done
        time_left = datetime.timedelta(seconds=(work_left / work_completion_rate))
        eta = datetime.datetime.now() + time_left
        if eta.day == datetime.datetime.now().day:
            # if current day then don't write complete date
            eta_str = eta.strftime("%H:%M:%S")
        else:
            # if different day then write complete date
            eta_str = eta.strftime("%d/%m/%Y %H:%M:%S")
        if time_left.total_seconds() < 60:
            time_left_str = f"{int(time_left.total_seconds())} seconds"
        else:
            time_left_str = str(time_left).split(".")[0]
        self.log_txt(f"estimated time left is: {time_left_str}\neta is: {eta_str}")

    @abc.abstractmethod
    def run_simulation(self):
        pass

    def force_stop(self):
        self.simulation_module.force_stop()


class ConductorThatWritesToFile(Conductor):
    class Flavor(enum.Enum):
        WRITE_PLANE_STATES = 0
        WRITE_LOCATION_INTERPOLATION = 1
        WRITE_LOCATION_INTERPOLATION_AND_VELOCITY = 2

    user_time_between_file_writings: int
    dataoutput_path: str
    start_of_output_file_names: str
    flavor: Flavor

    def __init__(self, simulation_module: SimulationModule, flavor: Flavor, dataoutput_path: str, user_time_between_file_writings: int,
                 log_file_fullname: str = None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.flavor = flavor
        self.dataoutput_path = dataoutput_path
        self.user_time_between_file_writings = user_time_between_file_writings

    def run_simulation(self):
        self.log_that_run_started()
        while not self.simulation_module.b_end_of_simulation_reached:
            system_states_to_print = self.simulation_module.calculate_next_ball_dynamics(
                user_time_timeout__sec=self.user_time_between_file_writings)[0]
            if self.flavor == ConductorThatWritesToFile.Flavor.WRITE_PLANE_STATES:
                StatesToFileWritingModule.add_plane_states_to_file(system_states_to_print, self.dataoutput_path, self.log_txt)
            if self.flavor == ConductorThatWritesToFile.Flavor.WRITE_LOCATION_INTERPOLATION:
                StatesToFileWritingModule.add_location_interpolation_map_to_file(system_states_to_print, self.dataoutput_path, self.log_txt)
        self.log_that_run_ended()


class ConductorWithNoOutput(Conductor):
    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, simulation_time_timeout=None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        if simulation_time_timeout is not None:
            self.simulation_module.halt_condition = HaltConditions.HaltAtGivenSimulationTime(
                simulation_time_timeout)

    def run_simulation(self):
        self.log_that_run_started()
        self.simulation_module.calculate_next_ball_dynamics()
        self.log_that_run_ended()


class ConductorWithProgressBar(Conductor):
    origional_halt_condition : HaltConditions

    def __init__(self, simulation_module: SimulationModule, simulation_time_timeout=None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=None)
        self.simulation_time_timeout = simulation_time_timeout
        if simulation_time_timeout is not None:
            self.origional_halt_condition = self.simulation_module.halt_condition
            self.simulation_module.halt_condition = self.simulation_module.halt_condition.add_halt_condition(
                HaltConditions.HaltAtGivenSimulationTime(simulation_time_timeout))

    def run_simulation(self):
        start_time = time()
        self.log_that_run_started()
        while not self.simulation_module.b_end_of_simulation_reached:
            self.simulation_module.calculate_next_ball_dynamics(user_time_timeout__sec=10)
            if not self.simulation_module.b_end_of_simulation_reached:
                self.log_eta(total_work=self.simulation_time_timeout, work_done=self.simulation_module.time, time_elapsed=time() - start_time)
        self.log_that_run_ended()
        self.simulation_module.halt_condition = self.origional_halt_condition


class ConductorThatAnimatesOnScreen(Conductor):
    max_time_calculation_is_ahead_of_animation: float
    simulation_animator: SimulationAnimator
    b_write_to_files: bool

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, target_fps: float = 30.0,
                 max_time_calculation_is_ahead_of_animation: float = 10.0, max_num_of_past_system_states: int = 60, simulation_time_timeout=None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.max_time_calculation_is_ahead_of_animation = max_time_calculation_is_ahead_of_animation
        self.target_fps = target_fps
        self.animation_time = 0
        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.b_is_first_frame = True

    '''
     this function calculates the next ball dynamics 
    '''

    def __simulation_states_producer_routine(self):
        while not self.simulation_module.b_end_of_simulation_reached:
            start_time_of_bulk = time()
            new_system_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(
                simulation_time_timeout=self.simulation_animator.animation_time + self.max_time_calculation_is_ahead_of_animation,
                user_time_timeout__sec=10 / self.target_fps)
            calculation_time_of_bulk = time() - start_time_of_bulk
            self.log_txt(f"calculated next {num_of_new_states} states in {calculation_time_of_bulk}")
            self.simulation_animator.add_new_states(new_system_states)
            sleep_time = 1 / self.target_fps - (time() - start_time_of_bulk)
            if sleep_time > 0.01:
                self.log_txt(f"sleep for {sleep_time}")
                sleep(sleep_time)
        self.log_that_run_ended()

    def run_simulation_module_on_other_thread(self):
        self.simulation_module_thread = threading.Thread(target=self.__simulation_states_producer_routine)
        self.simulation_module_thread.start()

    def run_simulation(self):
        self.simulation_animator = SimulationAnimator(self.simulation_module, target_fps=self.target_fps,
                                                      max_num_of_past_system_states=self.max_num_of_past_system_states,
                                                      write_to_log_func=self.log_txt)
        self.run_simulation_module_on_other_thread()
        self.animation_object = self.simulation_animator.start_animation_on_screen()


class ConductorThatAnimatesToFile(ConductorThatAnimatesOnScreen):
    origional_halt_condition: HaltConditions

    def __init__(self, simulation_module: SimulationModule, target_fps, length_seconds, file_name, b_halt_simulation_when_animation_ends=True, **kwargs):
        super(ConductorThatAnimatesToFile, self).__init__(
            simulation_module, **kwargs)
        self.fps = target_fps
        self.file_name = file_name
        self.length_seconds = length_seconds
        self.origional_halt_condition = self.simulation_module.halt_condition
        if b_halt_simulation_when_animation_ends:
            self.simulation_module.halt_condition = self.simulation_module.halt_condition.add_halt_condition(HaltConditions.HaltAtGivenSimulationTime(
                length_seconds + self.simulation_module.time))

    def run_simulation(self):
        self.simulation_animator = ToFileSimulationAnimationSaver(self.simulation_module, target_fps=self.target_fps,
                                                                  max_num_of_past_system_states=self.max_num_of_past_system_states,
                                                                  write_to_log_func=self.log_txt, write_eta_to_log_func=self.log_eta)
        self.run_simulation_module_on_other_thread()
        self.animation_object = self.simulation_animator.save_animation_to_file(file_name=self.file_name, length_seconds=self.length_seconds)
        self.simulation_module.halt_condition = self.origional_halt_condition


class MultiProcessConductorThatAnimatesOnScreen(Conductor):
    max_time_calculation_is_ahead_of_animation: float
    simulation_animator: SimulationAnimator
    write_to_file_conductor: ConductorThatWritesToFile

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, target_fps: float = 30.0,
                 max_time_calculation_is_ahead_of_animation: float = 10.0, max_num_of_past_system_states: int = 60, simulation_time_timeout=None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.max_time_calculation_is_ahead_of_animation = max_time_calculation_is_ahead_of_animation
        self.target_fps = target_fps
        self.animation_time = 0
        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.b_is_first_frame = True
        self.temp_files_path_names = os.getcwd().replace("\\", "/") + "temp_for_animation/" + str(np.random.randint(0, 10000)) + "temp"
        self.write_to_file_conductor = ConductorThatWritesToFile(self.simulation_module, flavor=ConductorThatWritesToFile.Flavor.WRITE_LOCATION_INTERPOLATION,
                                                                 dataoutput_path=self.temp_files_path_names,
                                                                 user_time_between_file_writings=10)

    def run_simulation(self):
        # TODO: clear files at self.temp_files_path_names

        if not os.path.exists(os.path.dirname(self.temp_files_path_names)):
            os.mkdir(os.path.dirname(self.temp_files_path_names))
        self.simulation_module.save_to_pickle(self.temp_files_path_names)

        # for windows cmd:
        command_text = f"START python -m src.DrawingModule.run_simulation_animator_from_files \"{self.temp_files_path_names}\" {self.target_fps} {self.max_num_of_past_system_states}"
        print("command is: ", command_text)
        os.system(command_text)

        self.write_to_file_conductor.run_simulation()
