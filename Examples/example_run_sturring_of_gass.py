from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np

bl1 = Ball([0.0, 0.0], [2, 0.0], 0.5, mass=10, color="#82242b")
bl2 = Ball([-0.8, 0.1], [5, 0], 0.2, color="#1b7a4e")
bl3 = Ball([-0.8, -0.8], [5, 0], 0.1, color="#875314")

boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [bl1,bl2,bl3]

simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation)
conductor.run_simulation()