import os

import numpy as np
import json
from .SystemState import SystemState
from typing import List, Dict


def add_plane_states_to_file(states: List[SystemState], path: str, write_to_log_func):
    text = "\n"
    for s in states:
        text += "State:\n"
        text += f"time:{s.time}\n"
        text += "locations:\n"
        for loc in s.balls_location:
            text += f"({loc[0]},{loc[1]})\n"
        for vel in s.balls_velocity:
            text += f"({vel[0]},{vel[1]})\n"

    path_new = path + "temp"
    with open(path_new, mode="a+") as f:
        f.write(text)
    write_to_log_func(f"wrote to {path_new}")


def add_location_interpolation_map_to_file(states: List[SystemState], path: str, write_to_log_func):
    if len(states) == 0:
        return
    np_arrays_dict = add_system_states_to_interpretation(states)
    path_new = find_empty_file_name(path,"npz")
    if not os.path.exists(os.path.dirname(path_new)):
        os.mkdir(os.path.dirname(path_new))
    np.savez(path_new, **np_arrays_dict)
    write_to_log_func(f"wrote to {path_new}")


def add_system_states_to_interpretation(system_states: List[SystemState]) -> Dict[str, np.ndarray]:
    if len(system_states) == 0:
        raise ValueError()
    num_of_balls = len(system_states[0].balls_radii)
    times_for_interp = np.full(len(system_states), np.nan)
    balls_locations_for_interp_x = np.full((len(system_states), num_of_balls), np.nan)
    balls_locations_for_interp_y = np.full((len(system_states), num_of_balls), np.nan)
    for i in range(len(system_states)):
        times_for_interp[i] = system_states[i].time
        for ball_index in range(len(system_states[i].balls_location)):
            balls_locations_for_interp_x[i, ball_index] = system_states[i].balls_location[ball_index][0]
            balls_locations_for_interp_y[i, ball_index] = system_states[i].balls_location[ball_index][1]
    return {"times_for_interp": times_for_interp,
            "balls_locations_for_interp_x": balls_locations_for_interp_x,
            "balls_locations_for_interp_y": balls_locations_for_interp_y}


def find_empty_file_name(path,extention):
    i = 0
    while True:
        new_path = path + str(i) + "." + extention
        if not os.path.exists(new_path):
            return new_path
        i += 1