import numpy as np
import matplotlib.pyplot as plt
import time

def adaptive_sample(function_to_sample,start,stop,num_of_points,f_kwargs=None,b_debug=False,b_print_progress=True,**kwargs):
    """
    algorithm in short: go to longest line, split in two, repeat.
    :param start:
    :param stop:
    :param num_of_points:
    :return:
    """
    f_kwargs = f_kwargs or dict()
    f_kwargs.update(kwargs)
    start_time = time.time()
    points_x = [start,stop]
    points_y,uncertainties_y = zip(*[function_to_sample(p_x,**f_kwargs) for p_x in points_x])
    points_y,uncertainties_y = list(points_y),list(uncertainties_y)
    return _rec_adaptive_sample(function_to_sample,f_kwargs,points_x,points_y,uncertainties_y,final_num_of_points = num_of_points,b_debug=b_debug,b_print_progress=b_print_progress,start_time=start_time)


def _rec_adaptive_sample(function_to_sample,f_kwargs,points_x,points_y,uncertainties_y,final_num_of_points,b_debug,b_print_progress,start_time):
    if final_num_of_points <= len(points_x):
        return points_x,points_y,uncertainties_y
    x_axis_length = points_x[-1] - points_x[0]
    y_axis_length = max(points_y) - min(points_y)
    distances = (np.diff(points_x)/x_axis_length)**2 + (np.diff(points_y)/y_axis_length)**2
    index_to_add_to = np.argmax(distances)
    new_point_x = (points_x[index_to_add_to] + points_x[index_to_add_to + 1])/2
    p_y,p_y_uncertainty = function_to_sample(new_point_x,**f_kwargs)
    points_x.insert(index_to_add_to + 1,new_point_x)
    points_y.insert(index_to_add_to + 1,p_y)
    uncertainties_y.insert(index_to_add_to + 1,p_y_uncertainty)
    if b_print_progress:
        part_of_work_done = len(points_x)/final_num_of_points
        time_left = (time.time()-start_time)*(1-part_of_work_done)/part_of_work_done
        print("{:03d}%, eta: {:0.5g} seconds".format(int(part_of_work_done*100),time_left))
    if b_debug:
        plt.clf()
        plt.errorbar(points_x,points_y,uncertainties_y, fmt="o")
        plt.pause(0.00001)
    return _rec_adaptive_sample(function_to_sample,f_kwargs,points_x,points_y,uncertainties_y,final_num_of_points,b_debug,b_print_progress=b_print_progress,start_time=start_time)