from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np

balls_arr = [Ball([x,y],[x,y],0.1) for x in (-0.5,0.5) for y in (-0.5,0.5)]
boundery = SlipperyBounceBounderyConditions_2D()

simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
# conductor = ConductorThatAnimatesOnScreen_OLD(simulation_module=simulation)
conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=60.0)
conductor.run_simulation()
