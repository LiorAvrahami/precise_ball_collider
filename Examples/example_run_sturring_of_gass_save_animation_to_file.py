from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D
from src.Conductor import ConductorThatAnimatesOnScreen, ConductorThatAnimatesToFile
import numpy as np

bl1 = Ball([0.0, 0.0], [0.2, 0.0], 0.5, mass=10, color="#82242b")
bl2 = Ball([-0.8, 0.1], [0.5, 0], 0.2, color="#1b7a4e")
bl3 = Ball([-0.8, -0.8], [0.5, 0], 0.1, color="#875314")

boundery = SlipperyBounceBounderyConditions_2D()
balls_arr = [bl1,bl2,bl3]

simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
simulation.calculate_next_ball_dynamics(11.7)
simulation.time = 0
conductor = ConductorThatAnimatesToFile(simulation_module=simulation,fps=30,file_name=r'E:\Liors_Stuff\Programing\python\precise_ball_collider\anim.gif')
conductor.run_simulation()