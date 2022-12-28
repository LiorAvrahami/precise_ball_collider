from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import *
from src.HaltConditions import HaltAtGivenSimulationTime
import numpy as np

boundery = SlipperyBounceBounderyConditions_2D()
sqrt_of_num_of_balls = 6

radius = 1 / (2 * sqrt_of_num_of_balls)
balls_arr = []
for x in np.linspace(-1, 1, sqrt_of_num_of_balls + 1, endpoint=False)[1:]:
    for y in np.linspace(-1, 1, sqrt_of_num_of_balls + 1, endpoint=False)[1:]:
        balls_arr.append(Ball((x, y), (0.5, 0), radius=radius, mass=1))
balls_arr[0].color = (0.8, 0.2, 0.2)
balls_arr[0].velocity[1] = 0.001
simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
# # conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=100)
# # conductor = MultiProcessConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=100)
# conductor1 = ConductorWithProgressBar(simulation_module=simulation, simulation_time_timeout=10)
# conductor1.run_simulation()
conductor2 = ConductorThatAnimatesToFile(simulation_module=simulation, target_fps=100, length_seconds=3, file_name=__file__ + ".gif")
conductor2.run_simulation()
