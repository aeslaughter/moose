#!/usr/bin/env python
import sys, os
import glob
import numpy as np
import math
import pandas
import matplotlib.pyplot as plt

fontsize = 16


# The csv files to read
filenames = glob.glob('level_set_mms*.csv')

# Extract the data
n = len(filenames)
error = np.zeros(n)
length = np.zeros(n)
for i, filename in enumerate(filenames):
    csv = pandas.read_csv(filename)
    error[i] = csv['error'].iloc[-1]
    length[i] = csv['h'].iloc[-1]

# Create figure and axes
fig = plt.figure(facecolor='w')
ax = plt.subplot(111, xscale='log', yscale='log')

ax.grid(True, which='major')
ax.grid(True, which='minor')

h = ax.plot(error, length, '-bo', markersize=5)

ax.set_xlabel('Element Length', fontsize=fontsize)
ax.set_ylabel('L2 Error', fontsize=fontsize)
for tick in ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(fontsize)
coefficients = np.polyfit(np.log10(length), np.log10(error), 1)

x = min(h[0].get_xdata())
y = max(h[0].get_ydata())
ax.text(x, y, 'slope = {}'.format(coefficients[0]), fontsize=15)
plt.show()
