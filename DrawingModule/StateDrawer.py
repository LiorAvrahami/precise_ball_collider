import matplotlib.pyplot as plt
from SystemState import SystemState
from typing import List, Tuple, Callable
import numpy as np
from Ball import Ball
from SimulationModule import SimulationModule

def draw_state(system_state: SystemState):
    ax = plt.subplots()[1]
    ax.clear()
    ax.add_artist(plt.text(0.02, 0.98, "", bbox={'facecolor': (0.35, 0.3, 0.2), 'alpha': 0.1, 'pad': 5}, va="top", alpha=0.9, transform=ax.transAxes))
    for i in range(len(system_state.balls_location)):
        ax.add_artist(plt.Circle(system_state.balls_location[i], system_state.balls_radii[i]))
    ax.set_xlim((-1, 1))
    ax.set_ylim((-1, 1))
    ax.set_aspect('equal')
