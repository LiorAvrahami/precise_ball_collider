import numpy as np
from Examples.experiment_gas_law_sparse.get_p import get_p
import matplotlib.pyplot as plt
from Examples.experiment_gas_law_sparse.plot_adaptive import adaptive_sample

SE = 0.01 ###
number_of_points_on_graph = 20 ###
number_of_balls = 20
max_number_of_balls_1d = int(np.ceil(number_of_balls**0.5))
ball_radius = 1
temperature = 1

start = (ball_radius*2*max_number_of_balls_1d)**2*1.001
stop = start * 1.3

volumes,pressures,pressures_uncertainties = adaptive_sample(get_p,start,stop,num_of_points=number_of_points_on_graph,temperature=temperature,
                                                            number_of_balls=number_of_balls,ball_radius=ball_radius,acceptable_relative_uncertainty=SE,b_debug=False)
plt.errorbar(volumes,pressures,pressures_uncertainties,fmt="o")
plt.xlim(0,max(volumes)*1.05)
plt.ylim(0,max(pressures)*1.05)