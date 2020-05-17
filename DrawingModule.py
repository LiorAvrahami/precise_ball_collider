import matplotlib.patches as patches
import matplotlib.pyplot as plt
from SystemState import SystemState
from time import time as get_current_real_time
from typing import List, Tuple, Callable
import numpy as np
from Ball import Ball
from SimulationModule import SimulationModule
from matplotlib import animation

FrameUpdate = List[plt.Artist]

def print_balls(ball_arr,sim_time,end_of_cycle_time = None):
    ax = plt.subplots()[1]
    ax.clear()
    print("balls state at time",sim_time)
    for ball in ball_arr:
        print("location", ball.location, "vel", ball.velocity)
        ax.add_artist(plt.Circle(ball.location,ball.radius))
    ax.set_xlim((-1,1))
    ax.set_ylim((-1, 1))
    ax.set_aspect('equal')
    if end_of_cycle_time is None:
        end_of_cycle_time = get_current_real_time() + 0.001
    plt.pause(end_of_cycle_time - get_current_real_time())

class StateDrawer():
    balls_locations_for_interp_x: List[List[float]]
    balls_locations_for_interp_y: List[List[float]]
    times_for_interp: List[float]

    ax: plt.Axes
    ball_artist_objects: List[patches.Circle]
    all_artist_objects: List[plt.Artist]
    time_text_artist: plt.Text
    max_num_of_past_system_states: int
    write_to_log: Callable
    def __init__(self,sim_module: SimulationModule,max_num_of_past_system_states: int,write_to_log = print):
        self.ax = plt.subplots()[1]
        self.times_for_interp = []
        num_of_balls = len(sim_module.balls_arr)
        self.balls_locations_for_interp_x = [[] for i in range(num_of_balls)]
        self.balls_locations_for_interp_y = [[] for i in range(num_of_balls)]

        self.ball_artist_objects = [plt.Circle((0,0), ball.radius,color=ball.color) for ball in sim_module.balls_arr]
        for ball_art_object in self.ball_artist_objects:
            self.ax.add_artist(ball_art_object)

        self.max_num_of_past_system_states = max_num_of_past_system_states
        self.write_to_log = write_to_log
        #missing boundery data TODO
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.add_system_states_to_interpretation([SystemState.generate_from_balls_array(sim_module.time,None,sim_module.balls_arr)])

        self.time_text_artist = plt.text(0.02,0.98,"",bbox={'facecolor':(0.35,0.3,0.2), 'alpha':0.1,'pad':5},va="top",alpha=0.9,transform = self.ax.transAxes)
        self.ax.add_artist(self.time_text_artist)
        self.all_artist_objects = self.ball_artist_objects + [self.time_text_artist]

    def add_system_states_to_interpretation(self,system_states:List[SystemState]):
        for state in system_states:
            self.times_for_interp.append(state.time)
            for ball_index in range(len(state.balls_location)):
                self.balls_locations_for_interp_x[ball_index].append(state.balls_location[ball_index][0])
                self.balls_locations_for_interp_y[ball_index].append(state.balls_location[ball_index][1])

    def handle_clearing_of_past_system_states(self,cur_animation_time):
        num_of_states_to_remove = sum([interp_time < cur_animation_time for interp_time in self.times_for_interp]) - self.max_num_of_past_system_states
        if num_of_states_to_remove >= 1:
            del self.times_for_interp[0:num_of_states_to_remove - 1]
            for ball_index in range(len(self.balls_locations_for_interp_x)):
                del self.balls_locations_for_interp_x[ball_index][0:num_of_states_to_remove - 1]
                del self.balls_locations_for_interp_y[ball_index][0:num_of_states_to_remove - 1]
        pass

    def draw_state_at_time(self, animation_time, end_of_cycle_time = None,b_plot=False):
        for ball_index in range(len(self.balls_locations_for_interp_x)):
            interpreted_x = np.interp(animation_time, self.times_for_interp, self.balls_locations_for_interp_x[ball_index],left=np.inf,right=np.inf)
            interpreted_y = np.interp(animation_time, self.times_for_interp, self.balls_locations_for_interp_y[ball_index],left=np.inf,right=np.inf)
            if interpreted_x == np.inf or interpreted_y == np.inf:
                raise Exception("animation time managed to exit scope of simulation times")
            self.ball_artist_objects[ball_index].center = (interpreted_x,interpreted_y)
            # self.ax.add_artist(plt.Circle((interpreted_x,interpreted_y), self.balls_radii[ball_index]))
        self.time_text_artist.set_text("time: " + "{:0.3g}".format(animation_time))
        if b_plot:
            if end_of_cycle_time is None:
                end_of_cycle_time = get_current_real_time() + 0.001
            self.write_to_log("print started")
            plt.pause(0.000001)
            self.write_to_log("print_ended")

    def update_animation(self,frame_data):
        new_system_states, time_to_print = frame_data
        self.add_system_states_to_interpretation(new_system_states)
        self.handle_clearing_of_past_system_states(time_to_print)
        self.draw_state_at_time(time_to_print, None, b_plot=False)
        return self.all_artist_objects

    def start_animation(self,frames_generator):
        fig = self.ax.figure
        anim = animation.FuncAnimation(fig, self.update_animation,frames=frames_generator, interval=0, blit=True)
        plt.show()