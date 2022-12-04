import threading

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from ..SystemState import SystemState
from time import time as get_current_real_time
from typing import List, Tuple, Callable, TYPE_CHECKING
import numpy as np
from ..SimulationModule import SimulationModule
# from .. import Conductor
from matplotlib import animation
from time import time, sleep
import os

FrameUpdate = List[plt.Artist]


class SimulationAnimator:
    balls_locations_for_interp_x: List[List[float]]
    balls_locations_for_interp_y: List[List[float]]
    times_for_interp: List[float]

    ax: plt.Axes
    ball_artist_objects: List[patches.Circle]
    all_artist_objects: List[plt.Artist]
    time_text_artist: plt.Text
    max_num_of_past_system_states: int
    write_to_log_func: Callable

    animation_time: float
    b_is_lagging: bool

    producer_consumer_lock: threading.Lock


    def __init__(self, sim_module: SimulationModule, target_fps, max_num_of_past_system_states: int, write_to_log_func=print):
        self.ax = plt.subplots()[1]
        self.times_for_interp = []
        num_of_balls = len(sim_module.balls_arr)
        self.balls_locations_for_interp_x = [[] for i in range(num_of_balls)]
        self.balls_locations_for_interp_y = [[] for i in range(num_of_balls)]
        self.animation_time = 0
        self.b_is_lagging = True
        self.producer_consumer_lock = threading.Lock()

        self.ball_artist_objects = [plt.Circle((0, 0), ball.radius, color=ball.color) for ball in sim_module.balls_arr]
        for ball_art_object in self.ball_artist_objects:
            self.ax.add_artist(ball_art_object)

        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.write_to_log_func = write_to_log_func
        self.target_fps = target_fps
        self.last_real_frame_start_time = time()
        self.last_partial_frame_start_time = time()

        self.boundary_drawer = sim_module.boundery.draw
        self.ax.set_xlim(*sim_module.boundery.x_limits)
        self.ax.set_ylim(*sim_module.boundery.y_limits)
        self.ax.set_aspect('equal')
        self.add_initial_interpolation_points(sim_module)

        self.time_text_artist = plt.text(0.02, 0.98, "", bbox={'facecolor': (0.35, 0.3, 0.2), 'alpha': 0.1, 'pad': 5}, va="top", alpha=0.9,
                                         transform=self.ax.transAxes)
        self.ax.add_artist(self.time_text_artist)
        self.all_artist_objects = self.ball_artist_objects + [self.time_text_artist]

    def add_initial_interpolation_points(self,sim_module):
        self.add_system_states_to_interpolation(
            [SystemState.generate_from_balls_array(time=sim_module.time, total_num_of_steps=sim_module.total_num_of_steps, current_objects_in_collision=None,
                                                   balls=sim_module.balls_arr)])

    def add_new_states(self, system_states: List[SystemState]):
        '''
        :param system_states: the system states to add
        this function is the thread safe wrapper of add_system_states_to_interpolation.
        '''
        with self.producer_consumer_lock:
            self.add_system_states_to_interpolation(system_states)

    def add_system_states_to_interpolation(self, system_states: List[SystemState]):
        for state in system_states:
            # assert that system states are added in order
            assert len(self.times_for_interp) == 0 or state.time >= self.times_for_interp[-1]
            self.times_for_interp.append(state.time)
            for ball_index in range(len(state.balls_location)):
                self.balls_locations_for_interp_x[ball_index].append(state.balls_location[ball_index][0])
                self.balls_locations_for_interp_y[ball_index].append(state.balls_location[ball_index][1])

    def handle_clearing_of_past_system_states(self, cur_animation_time):
        num_of_states_to_remove = sum([interp_time < cur_animation_time for interp_time in self.times_for_interp]) - self.max_num_of_past_system_states
        if num_of_states_to_remove >= 1:
            del self.times_for_interp[0:num_of_states_to_remove - 1]
            for ball_index in range(len(self.balls_locations_for_interp_x)):
                del self.balls_locations_for_interp_x[ball_index][0:num_of_states_to_remove - 1]
                del self.balls_locations_for_interp_y[ball_index][0:num_of_states_to_remove - 1]
        pass

    def draw_state_at_time(self, animation_time):
        for ball_index in range(len(self.balls_locations_for_interp_x)):
            interpreted_x = np.interp(animation_time, self.times_for_interp, self.balls_locations_for_interp_x[ball_index], left=np.inf, right=np.inf)
            interpreted_y = np.interp(animation_time, self.times_for_interp, self.balls_locations_for_interp_y[ball_index], left=np.inf, right=np.inf)
            if interpreted_x == np.inf or interpreted_y == np.inf:
                raise Exception(f"animation time managed to exit scope of simulation times {animation_time} {self.times_for_interp[-1]}")
            self.ball_artist_objects[ball_index].center = (interpreted_x, interpreted_y)
            # self.ax.add_artist(plt.Circle((interpreted_x,interpreted_y), self.balls_radii[ball_index]))
        self.time_text_artist.set_text("time: " + "{:0.3g}".format(animation_time))

    def update_animation(self, frame):

            last_partial_frame_time_interval = (time() - self.last_partial_frame_start_time)
            self.last_partial_frame_start_time = time()

            # check if animation should change lagging state
            if self.animation_time + last_partial_frame_time_interval > self.times_for_interp[-1]:
                # calculation is lagging
                self.b_is_lagging = True
            if self.b_is_lagging and self.animation_time + 5 < self.times_for_interp[-1]:
                # calculation is no longer lagging
                self.b_is_lagging = False

            if not self.b_is_lagging:
                with self.producer_consumer_lock:
                    self.animation_time += last_partial_frame_time_interval
                    self.handle_clearing_of_past_system_states(self.animation_time)
                    self.draw_state_at_time(self.animation_time)
                    # diagnostics
                    last_frame_time_interval = (time() - self.last_real_frame_start_time)
                    self.last_real_frame_start_time = time()
                    self.print_load_status_to_log(last_frame_time_interval)
            else:
                self.write_to_log_func(f"------------- LAG -------------\nanimation_time:{self.animation_time},calc_time:{self.times_for_interp[-1]}")
                self.do_idle_work(idle_time=1 / self.target_fps - last_partial_frame_time_interval)
            return self.all_artist_objects


    def print_load_status_to_log(self, last_frame_time_interval):
        self.write_to_log_func(f"fps = {1 / last_frame_time_interval:.1f}")

    def start_animation_on_screen(self):
        fig = self.ax.figure
        self.boundary_drawer(self.ax)
        anim = animation.FuncAnimation(fig, self.update_animation, interval=1000/(self.target_fps*2.5), blit=True)
        plt.show()
        return anim

    def save_animation_to_file(self, frames_generator, fps, file_name):
        num_frames = None
        fig = self.ax.figure
        self.boundary_drawer(self.ax)
        anim = animation.FuncAnimation(fig, self.update_animation, frames=num_frames, blit=True)
        writervideo = animation.FFMpegWriter(fps=fps)
        anim.save(file_name, writer=writervideo)

    def do_idle_work(self, idle_time):
        if idle_time > 0:
            sleep(idle_time)


class FromFilesSimulationAnimator(SimulationAnimator):
    files_paths_generator = None
    next_file_name: str
    after_next_file_name: str

    def __init__(self, sim_module: SimulationModule, target_fps, max_num_of_past_system_states: int, files_paths_generator, **kwargs):
        super(FromFilesSimulationAnimator, self).__init__(sim_module, target_fps, max_num_of_past_system_states, **kwargs)
        self.files_paths_generator = files_paths_generator
        self.next_file_name = next(self.files_paths_generator)
        self.after_next_file_name = next(self.files_paths_generator)

    def do_idle_work(self, idle_time):
        start_time = time()
        while os.path.exists(self.after_next_file_name):# and idle_time > (time() - start_time):
            self.read_and_add_next_interpolation_map_file()

    def read_and_add_next_interpolation_map_file(self):
        a = np.load(self.next_file_name)
        vals = a.f
        times = vals.times_for_interp
        ball_x = vals.balls_locations_for_interp_x
        ball_y = vals.balls_locations_for_interp_y

        self.next_file_name = self.after_next_file_name
        self.after_next_file_name = next(self.files_paths_generator)

        self.add_interp_map_to_interpolation(times, ball_x, ball_y)

    def add_interp_map_to_interpolation(self, times, ball_x, ball_y):
        num_balls = ball_x.shape[1]
        for i in range(len(times)):
            # assert that system states are added in order
            assert len(self.times_for_interp) == 0 or times[i] >= self.times_for_interp[-1]
            self.times_for_interp.append(times[i])
            for ball_index in range(num_balls):
                self.balls_locations_for_interp_x[ball_index].append(ball_x[i, ball_index])
                self.balls_locations_for_interp_y[ball_index].append(ball_y[i, ball_index])
