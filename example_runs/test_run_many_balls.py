from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D,CyclicBounderyConditions_2D
from Conductor import Conductor_That_PrintsToScreen_OLD,Conductor_That_PrintsToScreen,Conductor_That_PrintsToScreen_Fast
import numpy as np

boundery = SlipperyBounceBounderyConditions_2D()
sqrt_of_num_of_balls = 5

radius = 1/(2*sqrt_of_num_of_balls)
dx = 2/(sqrt_of_num_of_balls)
balls_arr = []
for x_index in range(sqrt_of_num_of_balls):
    for y_index in range(sqrt_of_num_of_balls):
        balls_arr.append(Ball((dx*x_index-0.5 + 0.001*y_index,dx*y_index-0.5 + 0.001*x_index),(3,0.2),radius=radius,mass=1))
balls_arr[0].color = (0.8,0.2,0.2)
simulation = SimulationModule(boundery_conditions=boundery,balls_arr=balls_arr)
conductor = Conductor_That_PrintsToScreen_Fast(simulation_module=simulation,target_fps=30)
conductor.run_simulation()
