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

    producer_consumer_lock: threading.Lock

    def __init__(self, sim_module: SimulationModule, target_fps, max_num_of_past_system_states: int, write_to_log_func=print):
        self.ax = plt.subplots()[1]
        self.times_for_interp = []
        num_of_balls = len(sim_module.balls_arr)
        self.balls_locations_for_interp_x = [[] for i in range(num_of_balls)]
        self.balls_locations_for_interp_y = [[] for i in range(num_of_balls)]
        self.animation_time = 0
        self.producer_consumer_lock = threading.Lock()

        self.ball_artist_objects = [plt.Circle((0, 0), ball.radius, color=ball.color) for ball in sim_module.balls_arr]
        for ball_art_object in self.ball_artist_objects:
            self.ax.add_artist(ball_art_object)

        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.write_to_log_func = write_to_log_func
        self.target_fps = target_fps
        self.last_frame_start_time = time()

        self.boundary_drawer = sim_module.boundery.draw
        self.ax.set_xlim(*sim_module.boundery.x_limits)
        self.ax.set_ylim(*sim_module.boundery.y_limits)
        self.ax.set_aspect('equal')
        self.add_system_states_to_interpretation(
            [SystemState.generate_from_balls_array(time=sim_module.time, total_num_of_steps=sim_module.total_num_of_steps, current_objects_in_collision=None,
                                                   balls=sim_module.balls_arr)])

        self.time_text_artist = plt.text(0.02, 0.98, "", bbox={'facecolor': (0.35, 0.3, 0.2), 'alpha': 0.1, 'pad': 5}, va="top", alpha=0.9,
                                         transform=self.ax.transAxes)
        self.ax.add_artist(self.time_text_artist)
        self.all_artist_objects = self.ball_artist_objects + [self.time_text_artist]

    def add_new_states(self, system_states: List[SystemState]):
        '''
        :param system_states: the system states to add
        this function is the thread safe wrapper of add_system_states_to_interpretation.
        '''
        with self.producer_consumer_lock:
            self.add_system_states_to_interpretation(system_states)

    def add_system_states_to_interpretation(self, system_states: List[SystemState]):
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
                raise Exception("animation time managed to exit scope of simulation times")
            self.ball_artist_objects[ball_index].center = (interpreted_x, interpreted_y)
            # self.ax.add_artist(plt.Circle((interpreted_x,interpreted_y), self.balls_radii[ball_index]))
        self.time_text_artist.set_text("time: " + "{:0.3g}".format(animation_time))

    def update_animation(self, frame):
        with self.producer_consumer_lock:
            # update animation only if  simulation time is more advanced then simulation time
            if self.animation_time + 1 / self.target_fps < self.times_for_interp[-1]:
                self.animation_time += 1 / self.target_fps
                self.handle_clearing_of_past_system_states(self.animation_time)
                self.draw_state_at_time(self.animation_time)
                # diagnostics
                last_frame_time_interval = (time() - self.last_frame_start_time)
                self.last_frame_start_time = time()
                self.print_load_status_to_log(last_frame_time_interval)
        return self.all_artist_objects

    def print_load_status_to_log(self, last_frame_time_interval):
        self.write_to_log_func(f"fps = {1 / last_frame_time_interval:.1f}, "
                               f"slowing_factor = {last_frame_time_interval / self.target_fps:.1f}")

    def start_animation_on_screen(self):
        fig = self.ax.figure
        self.boundary_drawer(self.ax)
        anim = animation.FuncAnimation(fig, self.update_animation, interval=self.target_fps, blit=True)
        plt.show()
        return anim

    def save_animation_to_file(self, frames_generator, fps, file_name):
        num_frames = None
        fig = self.ax.figure
        self.boundary_drawer(self.ax)
        anim = animation.FuncAnimation(fig, self.update_animation, frames=num_frames, blit=True)
        writervideo = animation.FFMpegWriter(fps=fps)
        anim.save(file_name, writer=writervideo)
