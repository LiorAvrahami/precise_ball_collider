from Ball import Ball_2D , Ball
import numpy as np
from BounderyConditions import CyclicBounderyConditions_2D, BounceBounderyConditions_2D
from matplotlib import pyplot as plt


def calc_collision_time_between_balls(bl1:Ball, bl2:Ball):
    # math formula:
    # time = [-(v*r) +- sqrt{(vR)^2 - (vxr)}]/v^2
    # v = relative velocity vector; r = relative position vector; R = sum of radii
    v = bl1.velocity - bl2.velocity
    R = bl1.radius + bl2.radius
    r = bl1.location - bl2.location
    impact_param = np.dot(v,v)*R**2-np.cross(v,r)**2
    if impact_param > 0:
        impact_time = (-np.dot(v, r) - impact_param ** 0.5) / (np.dot(v,v))
        if impact_time < 0:
            impact_time = np.inf

    else:
        impact_time = np.inf
    return impact_time




def handle_collision(bl1:Ball,bl2:Ball):
    v = bl1.velocity - bl2.velocity
    r = bl1.location - bl2.location
    reduced_mass = 2*(bl2.mass)/(bl2.mass + bl1.mass)
    velocity_geometry_factor = (np.dot(v,r)/np.dot(r,r))*r
    bl1.velocity -= reduced_mass * velocity_geometry_factor
    bl2.velocity -= (reduced_mass - 2) * velocity_geometry_factor

ax = plt.subplots()[1]
def print_balls(ball_arr,time):
    ax.clear()
    print("balls state at time",time)
    for ball in ball_arr:
        print("location", ball.location, "vel", ball.velocity)
        ax.add_artist(plt.Circle(ball.location,ball.radius))
    ax.set_xlim((-1,1))
    ax.set_ylim((-1, 1))
    ax.set_aspect('equal')
    plt.pause(0.01)

time = 0
bl1 = Ball_2D([0.0,0.0],[1.0,0.0],0.5)
bl2 = Ball_2D([-0.8,0],[0.5,0],0.2)
boundery = BounceBounderyConditions_2D()
balls_arr = [bl1,bl2]
for i in range(100):# num of timesteps
    print_balls(ball_arr=balls_arr,time=time)
    next_possible_interupts = []
    for current_ball_index in range(len(balls_arr)):
        current_ball = balls_arr[current_ball_index]
        # collition with walls:
        collision_time, wall_index = boundery.calc_collision_time_with_walls(current_ball)
        if collision_time != None:
            next_possible_interupts.append((collision_time,boundery.handle_wall_collision,(current_ball,wall_index)))

        # collition with balls:
        for second_ball_index in range(current_ball_index + 1,len(balls_arr)):
            second_ball = balls_arr[second_ball_index]
            collision_time = calc_collision_time_between_balls(current_ball,second_ball)
            if collision_time != None:
                next_possible_interupts.append((collision_time, handle_collision, (current_ball, second_ball)))

    # next interupt is the one that happens firrst
    time_step_till_next_interupt, interupt_handler_function, handler_paramiters  = min(next_possible_interupts)
    if time_step_till_next_interupt > 0.06:
        time_step_till_next_interupt, interupt_handler_function, handler_paramiters = (0.05,None,None)
    # propagate balls
    for ball in balls_arr:
        ball.linear_propagate(time_step_till_next_interupt)
    time += time_step_till_next_interupt

    # handle couse of interupt (collition physics)
    if interupt_handler_function != None:
        interupt_handler_function(*handler_paramiters)







