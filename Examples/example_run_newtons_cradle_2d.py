from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np


R = 0.1
d_offset = R/(2**0.5)

balls_arr = [
    Ball([-0.7, d_offset], [0, 0], R),
    Ball([0.7, -d_offset], [0, 0], R),
    Ball([d_offset, -0.7], [0, 0], R),
    Ball([-d_offset, 0.7], [0, 0], R),
    Ball([-0.3, d_offset], [1, 0], R),
    Ball([0.3, -d_offset], [-1, 0], R)
]
boundery = SlipperyBounceBounderyConditions_2D()

simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
# conductor = ConductorThatAnimatesOnScreen_OLD(simulation_module=simulation)
conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=60.0)
conductor.run_simulation()
