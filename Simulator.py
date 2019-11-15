from Ball import Ball_2D , Ball
import numpy as np


def calc_collition_time(bl1:Ball,bl2:Ball):
    # math formula:
    # time = [-(v*r) +- sqrt{(vR)^2 - (vxr)}]/v^2
    # v = relative velocity vector; r = relative position vector; R = sum of radii
    v = bl1.velocity - bl2.velocity
    R = bl1.radius + bl2.radius
    r = bl1.location - bl2.location
    impact_param = np.dot(v,v)*R**2-np.cross(v,r)**2
    if impact_param >= 0:
        impact_time = (-np.dot(v,r)-impact_param**0.5)/(np.dot(v,v))
        if impact_time < 0:
            impact_time = (-np.dot(v, r) + 2 * impact_param ** 0.5) / (2 * np.dot(v, v))
            if impact_time < 0:
                impact_time = None
    else:
        impact_time = None
    return impact_time


def handle_collition(bl1:Ball,bl2:Ball):
    v = bl1.velocity - bl2.velocity
    r = bl1.location - bl2.location
    reduced_mass = 2*(bl2.mass)/(bl2.mass + bl1.mass)
    velocity_geometry_factor = (np.dot(v,r)/np.dot(r,r))*r
    bl1.velocity -= reduced_mass * velocity_geometry_factor
    bl2.velocity -= (reduced_mass - 2) * velocity_geometry_factor

def print_balls(ball_arr,time):
    print("balls state at time",time)
    for ball in ball_arr:
        print("location", ball.location, "vel", ball.velocity)

time = 0
bl1 = Ball_2D([0.0,0.0],[1.0,0.0],0.8)
bl2 = Ball_2D([0.0,-1.0],[0.0,1.0],0.2)

print_balls([bl1,bl2],time)
impact_time = calc_collition_time(bl1,bl2)
bl1.linear_propagate(impact_time)
bl2.linear_propagate(impact_time)
time += impact_time
print_balls([bl1,bl2],time)
handle_collition(bl1,bl2)
print_balls([bl1,bl2],time)
bl1.linear_propagate(10)
bl2.linear_propagate(10)
time += 10
print_balls([bl1,bl2],time)







