#!/usr/bin/env python
from matplotlib import pyplot as plt
import numpy as np
import glob
import pandas
import re


# Extract L2Error and NumDofs
x = []; y = []
filenames = glob.glob('olsson_2d_*.csv')
for fname in filenames:
    data = pandas.read_csv(fname)
    x.append(np.sqrt(data['ndofs'].iloc[-1]))
    y.append(np.sqrt(data['error'].iloc[-1]))

# Create the plot of computed error
fig = plt.figure()
fig.set_facecolor('white')
ax = plt.subplot(111)
ax.loglog(x, y, 'ob', linewidth=3, label='Computed')
ax.legend(loc='lower right')
ax.grid(True)
ax.grid(True, which='minor')
ax.set_xlabel('sqrt(n)')
ax.set_ylabel('L2 Error')

m,b = np.polyfit(np.log10(x), np.log10(y), 1)
print m

plt.show()
