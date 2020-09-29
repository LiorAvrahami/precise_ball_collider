from SimulationModule import SimulationModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from Conductor import ConductorWithNoOutput,Conductor_That_PrintsToScreen
import numpy as np
import math

def get_random_velocity(temperature):
    # energy should be 3/2*T
    speed = 2*(3/2*temperature)**0.5
    theta = np.random.uniform(0,math.tau)
    velocity = speed*np.sin(theta),speed*np.cos(theta)
    return np.array(velocity)

def calculate_pressure(wall_collisions_dt_array,wall_collisions_impulse_array,side_len):
    first_relevant_index = np.argmax(np.array(wall_collisions_dt_array)>0)+10
    relevant_impulse_measurements = np.array(wall_collisions_impulse_array[first_relevant_index:])
    relevant_dt_measurements = np.array(wall_collisions_dt_array[first_relevant_index:])
    total_impulse = np.sum(relevant_impulse_measurements)
    total_time = np.sum(relevant_dt_measurements)
    p_avr = (total_impulse / total_time) / (side_len * 4)

    relative_std_of_total_impulse = np.std(relevant_impulse_measurements, ddof=1) * len(relevant_impulse_measurements) ** 0.5 / total_impulse
    relative_std_of_total_dt = np.std(relevant_dt_measurements, ddof=1) * len(relevant_dt_measurements) ** 0.5 / total_time
    p_relative_uncertainty = (relative_std_of_total_impulse ** 2 + relative_std_of_total_dt ** 2) ** 0.5
    return p_avr, p_relative_uncertainty


def get_p(volume,temperature,number_of_balls,ball_radius,acceptable_relative_uncertainty,random_seed=None):
    p_avr = None
    p_relative_uncertainty = None
    wall_collisions_impulse_array = []
    wall_collisions_dt_array = []
    last_collision_time = 0
    def on_wall_collition(*args,wall_index,ball:Ball,**kwargs):
        nonlocal last_collision_time,p_avr,p_relative_uncertainty
        time = simulation.time
        dt = time - last_collision_time
        last_collision_time = time
        v_1d = ball.velocity[0] if wall_index in SlipperyBounceBounderyConditions_2D.wall_x_keys else ball.velocity[1]
        wall_collisions_impulse_array.append(abs(v_1d) * ball.mass * 2)
        wall_collisions_dt_array.append(dt)
        if len(wall_collisions_impulse_array) % 100 == 0:
            p_avr, p_relative_uncertainty = calculate_pressure(wall_collisions_dt_array,wall_collisions_impulse_array,side_len)
            if acceptable_relative_uncertainty > p_relative_uncertainty:
                conductor.force_stop()

    side_len = volume**0.5
    boundery = SlipperyBounceBounderyConditions_2D(wall_x_0=0,wall_x_1=side_len,wall_y_0=0,wall_y_1=side_len,on_wall_collision_event=on_wall_collition)
    ball_1d_locations = np.linspace(ball_radius,side_len-ball_radius,int(np.ceil(number_of_balls**0.5)))
    np.random.seed(random_seed)
    balls_arr = [Ball((x, y), get_random_velocity(temperature), ball_radius) for x in ball_1d_locations for y in ball_1d_locations][:number_of_balls]
    simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
    conductor = ConductorWithNoOutput(simulation_module=simulation)
    conductor.run_simulation()
    return p_avr,p_relative_uncertainty*p_avr