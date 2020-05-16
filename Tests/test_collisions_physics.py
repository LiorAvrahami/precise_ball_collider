from unittest import TestCase
from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D,CyclicBounderyConditions_2D,RectangleBoundery_2D
from Conductor import ConductorWithNoOutput,Conductor_That_PrintsToScreen_Fast
import numpy as np

class Test(TestCase):
    def assert_ball_is_in_bounds(self,ball,bounds:RectangleBoundery_2D):
        x,y = ball.location
        if x < bounds.wall_x_0 or x > bounds.wall_x_1 or y < bounds.wall_y_0 or y > bounds.wall_y_1:
            self.fail("ball escaped bounds: ball location = {},boundery = {}".format(ball.location,bounds))

    def test_multiple_instantaneous_collisions(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((-0.8, 0.5), (-1,0 ), 0.1)
        ball2 = Ball((0.8, 0.5), (1, 0), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1,ball2])
        conductor = ConductorWithNoOutput(simulation_time_timeout=0.5, simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(ball1,boundery)
        self.assert_ball_is_in_bounds(ball2, boundery)

    def test_collision_with_corner(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0.5, 0.5), (1, 1), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1])
        conductor = ConductorWithNoOutput(simulation_time_timeout=1, simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(ball1, boundery)