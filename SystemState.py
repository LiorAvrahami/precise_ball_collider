import numpy as np
from typing import List, Optional
from Ball import Ball


class SystemState:
    time: float
    current_objects_in_collision = None
    balls_location: np.ndarray
    balls_radii: np.ndarray
    balls_velocity: np.ndarray
    balls_angle: np.ndarray
    balls_angular_velocity: np.ndarray
    balls_id: np.ndarray
    balls_colors: list
    total_num_of_steps: int

    def propagate_by(self, time):
        new = self.clone()
        new.balls_location += new.balls_velocity * time
        new.time += time
        return new

    def clone(self):
        new = SystemState()
        new.time = self.time
        new.current_objects_in_collision = self.current_objects_in_collision
        new.balls_location = np.array(self.balls_location)
        new.balls_velocity = np.array(self.balls_velocity)
        new.balls_angle = np.array(self.balls_angle)
        new.balls_angular_velocity = np.array(self.balls_angular_velocity)
        new.balls_id = np.array(self.balls_id)
        new.total_num_of_steps = self.total_num_of_steps
        return new

    def get_collision_description(self) -> str:
        ret_str = "not implemented"
        if self.current_objects_in_collision is None:
            ret_str = "description for collition of more than two objects is not implemented"
        if len(self.current_objects_in_collision) == 2:
            b1: Optional[Ball] = None
            b2: Optional[Ball] = None
            wall_key: object = None
            collider1 = "Non"
            collider2 = "Non"
            approximate_location = "Non"
            if type(self.current_objects_in_collision[0]) == Ball:
                b1 = self.current_objects_in_collision[0]
                if type(self.current_objects_in_collision[1]) == Ball:
                    b2 = self.current_objects_in_collision[1]
                else:
                    wall_key = self.current_objects_in_collision[1]
            elif type(self.current_objects_in_collision[1]) == Ball:
                b1 = self.current_objects_in_collision[1]
                b2 = None
                wall_key = self.current_objects_in_collision[0]
            if b1 is not None:
                collider1 = "ball: " + str(b1.id)
            if b2 is not None:
                # two ball interaction
                collider2 = "ball: " + str(b2.id)
                approximate_location = (b1.location + b2.location) / 2
            elif wall_key is not None:
                # ball and wall interaction
                collider2 = "wall: " + str(wall_key)
                approximate_location = b1.location
            ret_str = "interaction between " + collider1 + " and " + collider2 + ". at approximate coordinates: " + str(approximate_location)
        else:
            raise NotImplementedError("unrecognized collision type, please implement function - get_collision_description in class SystemState")
        return ret_str

    @staticmethod
    def generate_from_balls_array(time: float, total_num_of_steps: int, current_objects_in_collision, balls: List[Ball]):
        self = SystemState()
        self.time = time
        self.current_objects_in_collision = current_objects_in_collision
        self.balls_location = np.array([ball.location for ball in balls])
        self.balls_velocity = np.array([ball.velocity for ball in balls])
        self.balls_angle = np.array([ball.angle for ball in balls])
        self.balls_angular_velocity = np.array([ball.angular_vel for ball in balls])
        self.balls_id = np.array([ball.id for ball in balls])
        self.total_num_of_steps = total_num_of_steps
        self.balls_colors = [ball.color for ball in balls]
        self.balls_radii = [ball.radius for ball in balls]
        return self

    @staticmethod
    def generate_from_simulation_module(simulation_module, current_objects_in_collision):
        return SystemState.generate_from_balls_array(simulation_module.time, simulation_module.total_num_of_steps, current_objects_in_collision, simulation_module.balls_arr)

    def draw_state(self,boundery_condition=None):
        import DrawingModule
        DrawingModule.draw_state(self,boundery_condition)
