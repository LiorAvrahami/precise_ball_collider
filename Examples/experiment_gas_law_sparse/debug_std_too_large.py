import numpy as np
import Examples.experiment_gas_law_sparse.get_p as get_p
import matplotlib.pyplot as plt

pi,std_pi = zip(*[get_p.get_p(1,1,16,0.05,0.1) for i in range(5)])
pi = np.array(pi)
std_pi = np.array(std_pi)*pi

print(pi)
print("std {}".format(np.std(pi,ddof=1)))
plt.errorbar(range(len(pi)),pi,std_pi,fmt="o")
plt.hlines(np.mean(pi),0,len(pi),colors="r",linestyles="--")
plt.figure()
plt.hist(pi,30)