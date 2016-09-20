#!/usr/bin/env python
import sys, os
import glob
import numpy
import math
import pandas
import matplotlib.pyplot as plt

df = pandas.DataFrame(pandas.read_csv('levelset_mms_out.csv', index_col='time'))
print df

ax = df.plot(y='point')
plt.show()



"""
# Load tools from moose/python
sys.path.append(os.path.join('..', '..', '..', '..', 'python'))
from utils import CSVIO, ConvergencePlot

# The csv files to read
filenames = glob.glob('levelset_mms*.csv')
n = len(filenames)

# Extract the data
error = numpy.zeros(n)
sqrt_dofs = numpy.zeros(n)
for i in xrange(n):
    csv = CSVIO(filenames[i])
    error[i] = csv.getColumn('error')[-1]
    sqrt_dofs[i] = math.sqrt(csv.getColumn('dofs')[-1])


# Plot the data
graph = ConvergencePlot(sqrt_dofs, error, xlabel = 'sqrt(dofs)', ylabel='L2_Error')
graph.fit()
graph.save('convergence.pdf')
"""
