import abc
import threading

from .SimulationModule import SimulationModule
from src import HaltConditions
from .StatesToFileWritingModule import add_states_to_files, add_text_to_file
from time import time, sleep
from typing import List, Generator
from .DrawingModule import SimulationAnimator, FrameUpdate


class Conductor(abc.ABC):
    simulation_module: SimulationModule
    log_file_fullname: str

    def __init__(self, simulation_module: SimulationModule, b_write_log_data_to_screen: bool, log_file_fullname: str = None):
        self.simulation_module = simulation_module
        self.log_file_fullname = log_file_fullname
        self.b_write_log_data_to_screen = b_write_log_data_to_screen

    def log_txt(self, txt):
        if self.log_file_fullname is not None:
            add_text_to_file(txt, self.log_file_fullname)
        elif self.b_write_log_data_to_screen:
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

    @abc.abstractmethod
    def run_simulation(self):
        pass

    def force_stop(self):
        self.simulation_module.fource_stop()


class ConductorThatWritesToFile(Conductor):
    num_of_steps_betwean_file_writings: int
    dataoutput_path: str
    start_of_output_file_names: str

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str, dataoutput_path: str, num_of_steps_betwean_file_writings: int,
                 start_of_output_file_names: str = None, b_write_log_data_to_screen=False):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname,
                         b_write_log_data_to_screen=b_write_log_data_to_screen)
        self.dataoutput_path = dataoutput_path
        self.num_of_steps_betwean_file_writings = num_of_steps_betwean_file_writings
        self.start_of_output_file_names = start_of_output_file_names

    def run_simulation(self):
        self.log_that_run_started()
        while not self.simulation_module.b_end_of_simulation_reached:
            system_states_to_print = self.simulation_module.calculate_next_ball_dynamics(
                simulation_steps_timeout=self.num_of_steps_betwean_file_writings)[0]
            add_states_to_files(
                system_states_to_print, self.dataoutput_path, self.start_of_output_file_names)
        self.log_that_run_ended()


class ConductorWithNoOutput(Conductor):
    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, simulation_time_timeout=None, b_write_log_data_to_screen=False):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname,
                         b_write_log_data_to_screen=b_write_log_data_to_screen)
        if simulation_time_timeout is not None:
            self.simulation_module.halt_condition = HaltConditions.HaltAtGivenSimulationTime(
                simulation_time_timeout)

    def run_simulation(self):
        self.log_that_run_started()
        self.simulation_module.calculate_next_ball_dynamics()
        self.log_that_run_ended()


class ConductorThatAnimatesOnScreen(Conductor):
    max_time_calculation_is_ahead_of_animation: float
    simulation_animator: SimulationAnimator
    b_write_to_files: bool

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, target_fps: float = 30.0,
                 time_calculation_is_ahead_of_animation: float = 10.0, max_num_of_past_system_states: int = 60, simulation_time_timeout=None,
                 b_write_log_data_to_screen=True):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname,
                         b_write_log_data_to_screen=b_write_log_data_to_screen)
        self.time_calculation_is_ahead_of_animation = time_calculation_is_ahead_of_animation
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
                simulation_time_timeout=self.simulation_animator.animation_time + self.time_calculation_is_ahead_of_animation,
                user_time_timeout__sec=1 / self.target_fps)
            calculation_time_of_bulk = time() - start_time_of_bulk
            self.log_txt(f"calculated next {num_of_new_states} states in {calculation_time_of_bulk}\n\n")
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


class ConductorThatAnimatesOnScreen__OLD(Conductor):
    time_calculation_is_ahead_of_animation: float
    target_fps: float
    animation_time: float
    b_write_to_files: bool
    b_is_first_frame: bool

    animation_object = None

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, target_fps: float = 30.0,
                 time_calculation_is_ahead_of_animation: float = 10.0, max_num_of_past_system_states: int = 60, simulation_time_timeout=None,
                 b_write_log_data_to_screen=True):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname,
                         b_write_log_data_to_screen=b_write_log_data_to_screen)
        self.time_calculation_is_ahead_of_animation = time_calculation_is_ahead_of_animation
        self.target_fps = target_fps
        self.animation_time = 0
        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.b_is_first_frame = True

    def get_frames_generator(self) -> Generator[List[FrameUpdate], None, None]:
        # Todo: improve function readability

        self.log_that_run_started()
        anim_start_time = time()

        # calculate first few seconds of animation in order to overcome initial lag
        self.log_txt("calculating the first few collisions")
        new_system_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(
            simulation_time_timeout=self.animation_time + self.time_calculation_is_ahead_of_animation)
        self.log_txt("initial calculation: calculated first {} states in {}".format(
            num_of_new_states, time() - anim_start_time))
        yield new_system_states, self.animation_time
        new_system_states = []

        while not self.simulation_module.b_end_of_simulation_reached:
            # keep track of when this frame calculation started:
            frame_start_time = time()

            # if animation time overtook simulation time then we must lag the simulation and preform some "emergency calculations"
            if self.animation_time > self.simulation_module.time:
                new_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(
                    simulation_time_timeout=self.animation_time + 0.1)
                new_system_states.extend(new_states)
                self.log_txt("emergancy calculation: calculated next {} states in {}".format(
                    num_of_new_states, time() - frame_start_time))
                # reset frame start time so we don't take the time to do the emergency calculations into account
                frame_start_time = time()

            yield new_system_states, self.animation_time
            leftover_calculation_start_time = time()
            new_system_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(
                simulation_time_timeout=self.animation_time + self.time_calculation_is_ahead_of_animation,
                user_time_timeout__sec=1 / self.target_fps - (time() - frame_start_time))
            leftover_calculation_time = time() - leftover_calculation_start_time
            if 1 / self.target_fps - (time() - frame_start_time) > 0:
                sleep(1 / self.target_fps - (time() - frame_start_time))
            cycle_time = time() - frame_start_time
            self.animation_time += cycle_time
            if cycle_time != 0:
                self.log_txt("fps {}, frame_time {}".format(
                    str(1 / cycle_time), cycle_time))
            self.log_txt("leftover_time calculation: calculated next {} states in {}\n\n".format(
                num_of_new_states, leftover_calculation_time))
        self.log_that_run_ended()

    def run_simulation(self):
        global animation_object
        self.state_drawer = SimulationAnimator(self.simulation_module, max_num_of_past_system_states=self.max_num_of_past_system_states,
                                               write_to_log=self.log_txt)
        animation_object = self.state_drawer.start_animation_on_screen(
            frames_generator=self.get_frames_generator())


class ConductorThatAnimatesToFile(ConductorThatAnimatesOnScreen):
    def __init__(self, simulation_module: SimulationModule, fps, file_name, **kwargs):
        super(ConductorThatAnimatesToFile, self).__init__(
            simulation_module, **kwargs)
        self.fps = fps
        self.file_name = file_name

    def run_simulation(self):
        global animation_object
        self.state_drawer = SimulationAnimator(self.simulation_module, max_num_of_past_system_states=self.max_num_of_past_system_states,
                                               write_to_log=self.log_txt)
        animation_object = self.state_drawer.save_animation_to_file(
            frames_generator=self.get_frames_generator(), fps=self.fps, file_name=self.file_name)
