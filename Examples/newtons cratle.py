from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen
import numpy as np

boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [Ball((x,0),(0,0),0.06) for x in np.linspace(-0.5,0.5,8,endpoint=False)]
balls_arr[0].velocity[0] = 1
balls_arr[1].velocity[0] = 1
balls_arr[1].color = (1,0,0)
simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)

conductor = ConductorThatAnimatesOnScreen(simulation_module=simulation, target_fps=30)
conductor.run_simulation()
