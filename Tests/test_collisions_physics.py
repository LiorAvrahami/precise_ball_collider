from unittest import TestCase
from SimulationModule import SimulationModule
import DrawingModule
from Ball import Ball
from BounderyConditions import SlipperyBounceBounderyConditions_2D,CyclicBounderyConditions_2D,RectangleBoundery_2D
from Conductor import ConductorWithNoOutput,Conductor_That_PrintsToScreen
from typing import Union,Tuple
import HaltConditions
import numpy as np

class Test(TestCase):
    def assert_ball_is_in_bounds(self,ball,bounds:Union[RectangleBoundery_2D,Tuple]):
        x,y = ball.location
        if type(bounds) is RectangleBoundery_2D:
            bx0, bx1, by0, by1 = bounds.wall_x_0, bounds.wall_x_1, bounds.wall_y_0, bounds.wall_y_1
        else:
            bx0, bx1, by0, by1 = bounds
        if x < bx0 or x > bx1 or y < by0 or y > by1:
            self.fail("ball not in bounds: ball location = {},boundery = {}".format(ball.location,bounds))

    def assert_ball_is_in_position(self,ball,pos,error=0.0001):
        bounds = (pos[0]-error,pos[0]+error,pos[1]-error,pos[1]+error)
        self.assert_ball_is_in_bounds(ball,bounds)

    def assert_ball_not_in_position(self,ball,pos,error=0.0001):
        self.assertRaises(AssertionError,self.assert_ball_is_in_position,ball,pos,error)

    def test_collide_with_wall(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0,0), (1,0), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1],halt_condition=HaltConditions.HaltAtGivenSimulationTime(1.8))
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1,(0,0))

    def test_multiple_halt_conditions_1(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0,0), (1,0), 0.1)
        halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.4) | HaltConditions.HaltAtBallExitsRectangle((-1,-1),(0.5,1))
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1],halt_condition=halt_condition)
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1,(0.4,0))

    def test_multiple_halt_conditions_2(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0,0), (1,0), 0.1)
        halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.4) | HaltConditions.HaltAtBallExitsRectangle((-1,-1),(0.3,1))
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1],halt_condition=halt_condition)
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1,(0.3,0))

    def test_ball_collition_physics(self):
        ball1 = Ball((2**0.5/20, 0.9), (0, -1), 0.1)
        ball2 = Ball((-2**0.5/20, -0.9), (0, 1), 0.1)
        simulation = SimulationModule(balls_arr=[ball1,ball2])
        conductor = ConductorWithNoOutput(simulation_module=simulation,simulation_time_timeout=1.4-2**0.5/10)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1, (0.5, 2 ** 0.5 / 20))
        self.assert_ball_is_in_position(ball2, (-0.5, -2 ** 0.5 / 20))

    def test_multiple_instantaneous_ball_collisions(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((-0.5, 0.2), (0, -1), 0.1)
        ball2 = Ball((-0.5, -0.2), (0, 1), 0.1)
        ball3 = Ball((0.5, 0.2), (0, -1), 0.1)
        ball4 = Ball((0.5, -0.2), (0, 1), 0.1)
        start_positions = np.array([ball1.location,ball2.location,ball3.location,ball4.location])
        simulation1 = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1,ball2,ball3,ball4], halt_condition=HaltConditions.HaltAtGivenSimulationTime(0.2))
        simulation2 = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1, ball2, ball3, ball4], halt_condition=HaltConditions.HaltAtGivenSimulationTime(0.3))

        simulation1.calculate_next_ball_dynamics()
        self.assert_ball_is_in_position(ball1, start_positions[0])
        self.assert_ball_is_in_position(ball2, start_positions[1])
        self.assert_ball_is_in_position(ball3, start_positions[2])
        self.assert_ball_is_in_position(ball4, start_positions[3])

        simulation2.calculate_next_ball_dynamics()
        self.assert_ball_not_in_position(ball1, start_positions[0])
        self.assert_ball_not_in_position(ball2, start_positions[1])
        self.assert_ball_not_in_position(ball3, start_positions[2])
        self.assert_ball_not_in_position(ball4, start_positions[3])

    def test_multiple_instantaneous_wall_collisions(self):
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