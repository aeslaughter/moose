#!/usr/bin/env python
import sys, os
import pandas
from utils.ConvergencePlot import ConvergencePlot

data = pandas.read_csv('advection_mms_out.csv')
fig = ConvergencePlot(data['h'], data['error'], xlabel='Element Length', ylabel='L2 Error')
#fig.save('convergence.pdf')
fig.show()
