from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from Conductor import Conductor_That_PrintsToScreen
import numpy as np

boundery = SlipperyBounceBounderyConditions_2D()
sqrt_of_num_of_balls = 5

radius = 1 / (2 * sqrt_of_num_of_balls)
balls_arr = []
for x in np.linspace(-1, 1, sqrt_of_num_of_balls + 1, endpoint=False)[1:]:
    for y in np.linspace(-1, 1, sqrt_of_num_of_balls + 1, endpoint=False)[1:]:
        balls_arr.append(Ball((x + 0.001 * y, y + 0.001 * x), (0.5, 0), radius=radius, mass=1))
balls_arr[0].color = (0.8, 0.2, 0.2)
simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
conductor = Conductor_That_PrintsToScreen(simulation_module=simulation, target_fps=30)
conductor.run_simulation()
