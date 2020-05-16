from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D,CyclicBounderyConditions_2D
from Conductor import Conductor_That_PrintsToScreen
import numpy as np

bl = Ball([-0.8,-0.8],[2,0.1],0.1)
boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [bl]

simulation = SimulationModule(boundery_conditions=boundery,balls_arr=balls_arr)
# conductor = Conductor_That_PrintsToScreen_OLD(simulation_module=simulation)
conductor = Conductor_That_PrintsToScreen(simulation_module=simulation,target_fps=60.0)
conductor.run_simulation()