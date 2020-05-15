from SystemState import SystemState
from typing import List, Dict


def get_row_of_certin_data_type(sys_state: SystemState,data_type_key: str) -> str:
    if data_type_key == location_data_key :
        return str(sys_state.balls_location)[1: -1]
    elif data_type_key == velocity_data_key :
        return str(sys_state.balls_velocity)[1: -1]
    elif data_type_key == angle_data_key :
        return str(sys_state.balls_angle)[1: -1]
    elif data_type_key == angular_vel_data_key :
        return str(sys_state.balls_angular_velocity)[1: -1]
    elif data_type_key == collision_disc_data_key :
        return sys_state.get_collision_description()

location_data_key = "location"
velocity_data_key = "velocity"
angle_data_key = "angle"
angular_vel_data_key = "angular_vel"
collision_disc_data_key = "collision_disc"
data_keys = [location_data_key ,velocity_data_key ,angle_data_key ,angular_vel_data_key,collision_disc_data_key]

def system_states_to_data_strings(sys_states: List[SystemState]) -> Dict[str,str]:
    data_text_library = {}
    for cur_state in sys_states:
        for data_type_key in data_keys:
            row_text = ""
            # add new line
            if data_text_library[data_type_key] != "":
                row_text = '\n'
            # convert system_state data to row
            row_text += get_row_of_certin_data_type(sys_state = cur_state,data_type_key = data_type_key)
            data_text_library[data_type_key] += row_text
    return data_text_library

def add_text_to_file( text, file_full_name):
    file = open(file_full_name,"a+")
    file.write(text)

def add_states_to_files(states: List[SystemState], path: str, start_of_file_names: str):
    dictionary_of_rows = system_states_to_data_strings(states)
    for data_type_key in dictionary_of_rows.keys():
        text = dictionary_of_rows[data_type_key]
        add_text_to_file(text,path + start_of_file_names + data_type_key)