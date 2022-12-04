import os
import sys
from src.DrawingModule import simulation_animator
from src.SimulationModule import SimulationModule


def npz_file_generator(path):
    extention = "npz"
    i = 0
    while True:
        new_path = path + str(i) + "." + extention
        yield new_path
        i += 1


if __name__ == "__main__":
    temp_files_path_names = sys.argv[1]
    target_fps = float(sys.argv[2])
    max_num_of_past_system_states = int(sys.argv[3])
    sim_module = SimulationModule.load_from_pickle(temp_files_path_names)
    simulation_animator = simulation_animator.FromFilesSimulationAnimator(sim_module=sim_module,
                                                                          target_fps=target_fps,
                                                                          max_num_of_past_system_states=max_num_of_past_system_states,
                                                                          files_paths_generator=npz_file_generator(temp_files_path_names))
    simulation_animator.start_animation_on_screen()
