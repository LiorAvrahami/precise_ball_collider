from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D,CyclicBounderyConditions_2D
from Conductor import Conductor_That_PrintsToScreen,Conductor_That_PrintsToScreen_OLD
import numpy as np

bl1 = Ball([0.0,0.0],[0.2,0.0],0.5,mass=np.inf)
bl2 = Ball([-0.8,0.1],[0.5,0],0.2)
bl3 = Ball([-0.8,-0.8],[0.5,0],0.1)
boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [bl1,bl2,bl3]

simulation = SimulationModule(boundery_conditions=boundery,balls_arr=balls_arr)
conductor = Conductor_That_PrintsToScreen_OLD(simulation_module=simulation)
conductor.run_simulation()
