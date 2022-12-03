from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np

bl = Ball([-0.8, -0.8], [2, 0.1], 0.1)
boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [bl]

simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
# conductor = ConductorThatAnimatesOnScreen_OLD(simulation_module=simulation)
conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=60.0)
conductor.run_simulation()
