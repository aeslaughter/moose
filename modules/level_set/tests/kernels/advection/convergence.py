#!/usr/bin/env python
import sys, os
import glob
import pandas
from matplotlib import pyplot as plt
from utils.ConvergencePlot import ConvergencePlot

# Convergence Plot
data = pandas.read_csv('advection_mms_out.csv')
fig = ConvergencePlot(data['h'], data['error'], xlabel='Element Length', ylabel='L2 Error')
#fig.save('convergence.png')
fig.show()

"""
# Results
filenames = glob.glob('advection_mms_out_results*.csv')
fig = plt.figure(facecolor='w')
ax = plt.subplot(111)
for filename in filenames:
    data = pandas.read_csv(filename)
    ax.plot(data['x'], data['phi'])
plt.show()
"""
