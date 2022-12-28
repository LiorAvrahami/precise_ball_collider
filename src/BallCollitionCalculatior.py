from .Ball import Ball
import numpy as np


def calc_collision_time_between_balls(bl1: 'Ball', bl2: 'Ball'):
    # math formula:
    # minimal distance squared = (vxr)^2/v^2
    # [{(vR)^2 - (vxr)^2}]/v^2
    # impact_param/v = R - h
    # time = [-(v*r) +- sqrt{(vR)^2 - (vxr)^2}]/v^2
    # v = relative velocity vector; r = relative position vector; R = sum of radii
    v = bl1.velocity - bl2.velocity
    R = bl1.radius + bl2.radius
    r = bl1.location - bl2.location
    r_dot_v = np.dot(r, v)
    impact_param = np.dot(v, v) * R ** 2 - np.cross(v, r) ** 2
    if impact_param > 0 and r_dot_v < 0:
        impact_time = -(r_dot_v + impact_param ** 0.5) / (np.dot(v, v))
        assert impact_time > -0.000001 # impact_time < 0 means numerical error, we allow for small numerical error.
    else:
        impact_time = np.inf
    return impact_time


def handle_ball_collision(bl1: Ball, bl2: Ball):
    v = bl1.velocity - bl2.velocity
    r = bl1.location - bl2.location
    reduced_mass = 2 * (bl2.mass) / (bl2.mass + bl1.mass)
    velocity_geometry_factor = (np.dot(v, r) / np.dot(r, r)) * r
    bl1.velocity -= reduced_mass * velocity_geometry_factor
    bl2.velocity -= (reduced_mass - 2) * velocity_geometry_factor
