#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import pandas
import glob
import time

tdata = pandas.read_csv('output/olsson_2d_out_line_time.csv')

ax = plt.subplot(111)

r = 0.15
epsilon = 0.05
c = np.array([0.5, 0.5, 0])
x = np.linspace(0, 1, 200)
exact = 1./(1 + np.exp( (abs(x - 0.5) - r) / epsilon))

ax.plot(x, exact, '-k', linewidth=2)
plt.show(False)
plt.draw()
plt.pause(1)

for index, row in tdata.iterrows():
    filename = 'output/olsson_2d_out_line_{:04d}.csv'.format(int(row['timestep']))
    data = pandas.read_csv(filename)
    ax.plot(data['x'], data['phi'], alpha=0.5)
    plt.draw()
    plt.pause(0.1)


#ax.set_xlim([0.3, 0.4])
#ax.set_ylim([0.2, 0.8])

plt.show()
