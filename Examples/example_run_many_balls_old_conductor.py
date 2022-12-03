from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np

boundery = SlipperyBounceBounderyConditions_2D()
sqrt_of_num_of_balls = 5

radius = 1 / (2 * sqrt_of_num_of_balls)
dx = 2 / (sqrt_of_num_of_balls)
balls_arr = []
for x_index in range(sqrt_of_num_of_balls):
    for y_index in range(sqrt_of_num_of_balls):
        balls_arr.append(Ball((dx * x_index - 0.5 + 0.001 * y_index, dx * y_index - 0.5 + 0.001 * x_index), (0.3, 0.2), radius=radius, mass=1))
balls_arr[0].color = (0.8, 0.2, 0.2)
simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=1)
conductor.run_simulation()
