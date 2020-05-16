import abc
from SimulationModule import SimulationModule
from HultCondition import HultCondition
from StatesToFileWritingModule import add_states_to_files, add_text_to_file
from time import time,sleep
from typing import List,Generator
from DrawingModule import StateDrawer,FrameUpdate

class Conductor(abc.ABC):
    simulation_module: SimulationModule
    log_file_fullname: str
    halt_condition: HultCondition

    def __init__(self,simulation_module: SimulationModule,log_file_fullname: str = None):
        self.simulation_module = simulation_module
        self.log_file_fullname = log_file_fullname

    def log_txt(self,txt):
        if self.log_file_fullname is None:
            print(txt)
        else:
            add_text_to_file(txt,self.log_file_fullname)

    def log_that_run_started(self):
        self.log_txt("run started")

    def log_that_run_ended(self):
        self.log_txt("run ended")

    def log_that_wrote_to_files(self,file_short_names: List[str]):
        self.log_txt("wrote to" + str(file_short_names))

    def log_that_Error_occured(self, error_object: Exception):
        self.log_txt("error occured\\nerror type: " + str(type(error_object))+ "\\nerror messege" + str(error_object))

    @abc.abstractmethod
    def run_simulation(self):
        pass

class Conductor_That_WritesToFile(Conductor):
    num_of_steps_betwean_file_writings: int
    dataoutput_path: str
    start_of_output_file_names: str

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str, dataoutput_path: str, num_of_steps_betwean_file_writings: int, start_of_output_file_names:str = None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.dataoutput_path = dataoutput_path
        self.num_of_steps_betwean_file_writings = num_of_steps_betwean_file_writings
        self.start_of_output_file_names = start_of_output_file_names


    def run_simulation(self):
        self.log_that_run_started()
        while not self.simulation_module.was_halt_condition_met():
            system_states_to_print = self.simulation_module.calculate_next_ball_dynamics(simulation_steps_timeout=self.num_of_steps_betwean_file_writings)[0]
            add_states_to_files(system_states_to_print, self.dataoutput_path, self.start_of_output_file_names)
        self.log_that_run_ended()

class ConductorWithNoOutput(Conductor):
    simulation_time_timeout:float
    def __init__(self, simulation_time_timeout, simulation_module: SimulationModule, log_file_fullname: str=None):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.simulation_time_timeout = simulation_time_timeout

    def run_simulation(self):
        self.log_that_run_started()
        self.simulation_module.calculate_next_ball_dynamics(simulation_time_timeout=self.simulation_time_timeout)
        self.log_that_run_ended()

class Conductor_That_PrintsToScreen(Conductor):
    time_calculation_is_ahead_of_animation: float
    target_fps: float
    animation_time: float
    b_write_to_files: bool
    b_is_first_frame: bool

    def __init__(self, simulation_module: SimulationModule, log_file_fullname: str = None, target_fps: float = 30.0,
                 time_calculation_is_ahead_of_animation: float = 10.0, max_num_of_past_system_states: int = 60):
        super().__init__(simulation_module=simulation_module, log_file_fullname=log_file_fullname)
        self.time_calculation_is_ahead_of_animation = time_calculation_is_ahead_of_animation
        self.target_fps = target_fps
        self.animation_time = 0
        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.b_is_first_frame = True

    def get_frames_generator(self) -> Generator[List[FrameUpdate],None,None]:
        # Todo: improve function readability
        while True:
            self.frame_start_time = time()
            if self.animation_time > self.simulation_module.time:
                new_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(simulation_time_timeout=self.animation_time + 0.1)
                self.new_system_states.extend(new_states)
                self.log_txt("emergancy calculation: calculated next {} states in {}".format(num_of_new_states, time() - self.frame_start_time))
            self.state_drawer.add_system_states_to_interpretation(self.new_system_states)
            self.state_drawer.handle_clearing_of_past_system_states(self.animation_time)
            self.state_drawer.draw_state_at_time(self.animation_time, None, b_plot=False)
            yield self.state_drawer.all_artist_objects
            leftover_calculation_start_time = time()
            self.new_system_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(
                simulation_time_timeout=self.animation_time + self.time_calculation_is_ahead_of_animation, user_time_timeout__sec=1 / self.target_fps - (time() - self.frame_start_time))
            leftover_calculation_time = time() - leftover_calculation_start_time
            if 1 / self.target_fps - (time() - self.frame_start_time) > 0:
                sleep(1 / self.target_fps - (time() - self.frame_start_time))
            cycle_time = time() - self.frame_start_time
            self.animation_time += cycle_time
            if cycle_time != 0:
                self.log_txt("fps {}, frame_time {}".format(str(1 / cycle_time), cycle_time))
            self.log_txt("leftover_time calculation: calculated next {} states in {}\n\n".format(num_of_new_states, leftover_calculation_time))

    def run_simulation(self):
        self.state_drawer = StateDrawer(self.simulation_module,max_num_of_past_system_states = self.max_num_of_past_system_states,write_to_log = self.log_txt)
        self.log_that_run_started()
        self.new_system_states = []

        calc_start_time = time()
        self.log_txt("calculating the first few collisions")
        new_states, num_of_new_states = self.simulation_module.calculate_next_ball_dynamics(simulation_time_timeout=self.animation_time + self.time_calculation_is_ahead_of_animation)
        self.new_system_states.extend(new_states)
        self.log_txt("initial calculation: calculated first {} states in {}".format(num_of_new_states, time() - calc_start_time))
        self.state_drawer.add_system_states_to_interpretation(self.new_system_states)
        self.new_system_states = []

        frames_generator = self.get_frames_generator()
        def update_frame(i):
            return next(frames_generator)

        self.state_drawer.start_animation(update_func = update_frame)
        self.log_that_run_ended()