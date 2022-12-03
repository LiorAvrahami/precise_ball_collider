from unittest import TestCase
from src.SimulationModule import SimulationModule
import src.DrawingModule
from src.Ball import Ball
from src.BounderyConditions import SlipperyBounceBounderyConditions_2D, CyclicBounderyConditions_2D, RectangleBoundery_2D
from src.Conductor import ConductorWithNoOutput, ConductorThatAnimatesOnScreen
from typing import Union, Tuple
import src.HaltConditions
import numpy as np
import matplotlib.pyplot as plt


class Test(TestCase):
    def assert_ball_is_in_bounds(self, ball, bounds: Union[RectangleBoundery_2D, Tuple]):
        x, y = ball.location
        if isinstance(bounds, RectangleBoundery_2D):
            bx0, bx1, by0, by1 = bounds.wall_x_0, bounds.wall_x_1, bounds.wall_y_0, bounds.wall_y_1
        else:
            bx0, bx1, by0, by1 = bounds
        if x < bx0 or x > bx1 or y < by0 or y > by1:
            self.fail("ball not in bounds: ball location = {},boundery = {}".format(ball.location, bounds))

    def assert_ball_not_in_bounds(self, ball, bounds: Union[RectangleBoundery_2D, Tuple]):
        with self.assertRaises(AssertionError, msg="ball is in unexpected area: ball location = {},boundery = {}".format(ball.location, bounds)):
            self.assert_ball_is_in_bounds(ball, bounds)

    def assert_ball_is_in_position(self, ball, pos, error=0.0001):
        bounds = (pos[0] - error, pos[0] + error, pos[1] - error, pos[1] + error)
        self.assert_ball_is_in_bounds(ball, bounds)

    def assert_ball_not_in_position(self, ball, pos, error=0.0001):
        bounds = (pos[0] - error, pos[0] + error, pos[1] - error, pos[1] + error)
        self.assert_ball_not_in_bounds(ball, bounds)

    def test_collide_with_wall(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0, 0), (1, 0), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1], halt_condition=HaltConditions.HaltAtGivenSimulationTime(1.8))
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1, (0, 0))

    def test_multiple_halt_conditions_1(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0, 0), (1, 0), 0.1)
        halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.4) | HaltConditions.HaltAtBallExitsRectangle((-1, -1), (0.5, 1))
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1], halt_condition=halt_condition)
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1, (0.4, 0))

    def test_multiple_halt_conditions_2(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0, 0), (1, 0), 0.1)
        halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.4) | HaltConditions.HaltAtBallExitsRectangle((-1, -1), (0.3, 1))
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1], halt_condition=halt_condition)
        conductor = ConductorWithNoOutput(simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1, (0.3, 0))

    def test_ball_collition_physics(self):
        ball1 = Ball((2 ** 0.5 / 20, 0.9), (0, -1), 0.1)
        ball2 = Ball((-2 ** 0.5 / 20, -0.9), (0, 1), 0.1)
        simulation = SimulationModule(balls_arr=[ball1, ball2])
        conductor = ConductorWithNoOutput(simulation_module=simulation, simulation_time_timeout=1.4 - 2 ** 0.5 / 10)
        conductor.run_simulation()
        self.assert_ball_is_in_position(ball1, (0.5, 2 ** 0.5 / 20))
        self.assert_ball_is_in_position(ball2, (-0.5, -2 ** 0.5 / 20))

    def test_multiple_instantaneous_ball_collisions_hole_numbers(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((-0.5, 0.2), (0, -1), 0.1)
        ball2 = Ball((-0.5, -0.2), (0, 1), 0.1)
        ball3 = Ball((0.5, 0.2), (0, -1), 0.1)
        ball4 = Ball((0.5, -0.2), (0, 1), 0.1)
        start_positions = np.array([ball1.location, ball2.location, ball3.location, ball4.location])
        simulation1 = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1, ball2, ball3, ball4], halt_condition=HaltConditions.HaltAtGivenSimulationTime(0.2))

        simulation1.calculate_next_ball_dynamics()
        self.assert_ball_is_in_position(ball1, start_positions[0])
        self.assert_ball_is_in_position(ball2, start_positions[1])
        self.assert_ball_is_in_position(ball3, start_positions[2])
        self.assert_ball_is_in_position(ball4, start_positions[3])
        self.assertRaises(AssertionError, self.assert_ball_not_in_position, ball1, start_positions[0])

        simulation1.halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.3)
        simulation1.calculate_next_ball_dynamics()
        self.assert_ball_not_in_position(ball1, start_positions[0])
        self.assert_ball_not_in_position(ball2, start_positions[1])
        self.assert_ball_not_in_position(ball3, start_positions[2])
        self.assert_ball_not_in_position(ball4, start_positions[3])

    def test_multiple_instantaneous_ball_collisions_irrational_numbers(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        epsilon = 2 ** 0.5 / 10000000
        ball1 = Ball((-0.5, 0.2), (0, -1), 0.1)
        ball2 = Ball((-0.5, -0.2), (0, 1), 0.1)
        ball3 = Ball((0.5 + epsilon, 0.2 + epsilon), (0, -1), 0.1)
        ball4 = Ball((0.5 + epsilon, -0.2 + epsilon), (0, 1 + epsilon), 0.1)
        start_positions = np.array([ball1.location, ball2.location, ball3.location, ball4.location])
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1, ball2, ball3, ball4], halt_condition=HaltConditions.HaltAtGivenSimulationTime(0.2))

        simulation.calculate_next_ball_dynamics()
        simulation.draw_current_situation()
        self.assert_ball_is_in_position(ball1, start_positions[0])
        self.assert_ball_is_in_position(ball2, start_positions[1])
        self.assert_ball_is_in_position(ball3, start_positions[2])
        self.assert_ball_is_in_position(ball4, start_positions[3])
        self.assertRaises(AssertionError, self.assert_ball_not_in_position, ball1, start_positions[0])

        simulation.halt_condition = HaltConditions.HaltAtGivenSimulationTime(0.3)
        simulation.calculate_next_ball_dynamics()
        self.assert_ball_not_in_position(ball1, start_positions[0])
        self.assert_ball_not_in_position(ball2, start_positions[1])
        self.assert_ball_not_in_position(ball3, start_positions[2])
        self.assert_ball_not_in_position(ball4, start_positions[3])

    def test_multiple_instantaneous_wall_collisions(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((-0.8, 0.5), (-1, 0), 0.1)
        ball2 = Ball((0.8, 0.5), (1, 0), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1, ball2])
        conductor = ConductorWithNoOutput(simulation_time_timeout=0.5, simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(ball1, boundery)
        self.assert_ball_is_in_bounds(ball2, boundery)

    def test_collision_with_corner(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        ball1 = Ball((0.5, 0.5), (1, 1), 0.1)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=[ball1])
        conductor = ConductorWithNoOutput(simulation_time_timeout=1, simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(ball1, boundery)

    def test_many_collitions_1d(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        balls_arr = [Ball((-0.5, 0), (1.2, 0), 0.1),Ball((0.4, 0), (0.5, 0), 0.1)]
        balls_arr[0].mass *= 10000
        balls_arr[1].color = (1, 0, 0)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
        conductor = ConductorWithNoOutput(simulation_time_timeout=4,simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(balls_arr[0], boundery)
        self.assert_ball_is_in_bounds(balls_arr[1], boundery)

    def test_many_collitions_corner(self):
        boundery = SlipperyBounceBounderyConditions_2D()
        balls_arr = [Ball((0.2/np.sqrt(2) - 0.5,0.2/np.sqrt(2) - 0.5), (1.2, 1.2), 0.1),Ball((0.4,0.4), (0.5, 0.5), 0.1)]
        balls_arr[0].mass *= 10000
        balls_arr[1].color = (1, 0, 0)
        simulation = SimulationModule(boundery_conditions=boundery, balls_arr=balls_arr)
        conductor = ConductorWithNoOutput(simulation_time_timeout=4,simulation_module=simulation)
        conductor.run_simulation()
        self.assert_ball_is_in_bounds(balls_arr[0], boundery)
        self.assert_ball_is_in_bounds(balls_arr[1], boundery)



