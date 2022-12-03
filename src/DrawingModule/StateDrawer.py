import matplotlib.pyplot as plt
from ..SystemState import SystemState
from ..BounderyConditions import BounderyConditions
from typing import List, Tuple, Callable
import numpy as np
from ..Ball import Ball
from ..SimulationModule import SimulationModule


def draw_state(system_state: SystemState,boundery_condition:BounderyConditions=None, velocity_arrow_scale=10):
    ax = plt.subplots()[1]
    ax.clear()
    ax.add_artist(plt.text(0.02, 0.98, "time: " + "{}".format(system_state.time), bbox={'facecolor': (0.35, 0.3, 0.2), 'alpha': 0.1, 'pad': 5}, va="top", alpha=0.9, transform=ax.transAxes))
    for i in range(len(system_state.balls_location)):
        ax.add_artist(plt.Circle(system_state.balls_location[i], system_state.balls_radii[i], color=system_state.balls_colors[i]))
        # ax.arrow(x=system_state.balls_location[i][0], y=system_state.balls_location[i][1], dx=system_state.balls_velocity[i][0]*velocity_arrow_scale, dy=system_state.balls_velocity[i][1]*velocity_arrow_scale, width = arrow_width, color=(0.8, 0.2, 0.2, 0.4),edgecolor = "k",)
    ax.quiver(system_state.balls_location[:, 0], system_state.balls_location[:, 1], system_state.balls_velocity[:, 0], system_state.balls_velocity[:, 1], color=(0.8, 0.2, 0.2, 0.9), edgecolors="k",linewidths=0.4,
              zorder=2, angles='xy', scale_units='xy', scale=velocity_arrow_scale)
    if boundery_condition is not None:
        ax.set_xlim(*boundery_condition.x_limits)
        ax.set_ylim(*boundery_condition.y_limits)
        boundery_condition.draw(ax)
    else:
        ax.set_xlim((-1, 1))
        ax.set_ylim((-1, 1))
    ax.set_aspect('equal')
