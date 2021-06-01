#!/usr/bin/env python3
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import os
import argparse
import pandas
import matplotlib.pyplot as plt
import multiprocessing
import mooseutils

def plotter(prefix, suffix, xname, yname, xlabel=None, ylabel=None, xlog=None, ylog=None):
    """Show matplotlib plot of memory data"""

    fig = plt.figure(figsize=[4,4], dpi=300, tight_layout=True)
    ax = fig.subplots()

    for i, mode in enumerate(['normal', 'batch-restore', 'batch-reset']):
        data = pandas.read_csv('results/{}_{}.csv'.format(prefix, mode))
        ax.plot(data[xname], data[yname], label=mode, markersize=8, marker='osd'[i])

    if xlabel is not None:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel is not None:
        ax.set_ylabel(ylabel, fontsize=10)
    if xlog is not None:
        ax.set_xscale('log', base=xlog)
    if ylog is not None:
        ax.set_yscale('log', base=ylog)
    ax.grid(True, color=[0.7]*3)
    ax.grid(True, which='minor', color=[0.8]*3)
    ax.legend()

    outfile = '{}_{}.pdf'.format(prefix, suffix)
    fig.savefig(outfile)

if __name__ == '__main__':

    # Memory Serial
    plotter('full_solve_memory_serial', 'time',
            xname='n_samples', xlabel='Number of Simulations', xlog=10,
            yname='time', ylabel='Time (sec.)', ylog=10)

    plotter('full_solve_memory_serial', 'memory',
            xname='n_samples', xlabel='Number of Simulations', xlog=10,
            yname='total', ylabel='Memory (MiB)', ylog=10)

    # Memory Parallel
    plotter('full_solve_memory_parallel', 'time',
            xname='n_samples', xlabel='Number of Simulations', xlog=10,
            yname='time', ylabel='Time (sec.)', ylog=10)

    plotter('full_solve_memory_parallel', 'memory',
            xname='n_samples', xlabel='Number of Simulations', xlog=10,
            yname='per_proc', ylabel='Memory (MiB)', ylog=10)

    # Strong Scaling
    plotter('full_solve_strong_scale', 'strong',
            xname='n_ranks', xlabel='Number of Processors', xlog=2,
            yname='time', ylabel='Time (sec.)', ylog=10)




    """
    plotter('full_solve_memory_serial', LOCATION, '', EXT,
            ['normal', 'batch-restore', 'batch-reset'], ['total'], ['Total'], 'Memory (MiB)')

    plotter('full_solve_memory_mpi', LOCATION, 'time', EXT,
            ['normal', 'batch-restore', 'batch-reset'], ['time'], ['Time'], 'Time (sec.)')

    plotter('full_solve_memory_mpi', LOCATION, '', EXT,
            ['normal', 'batch-restore', 'batch-reset'], ['total', 'max_proc'], ['Total', 'Max'], 'Memory (MiB)')

    # Transient
    plotter('transient_memory_serial', LOCATION, 'time', EXT,
            ['normal', 'batch-restore'], ['time'], ['Time'], 'Time (sec.)')

    plotter('transient_memory_serial', LOCATION, '', EXT,
            ['normal', 'batch-restore'], ['total'], ['Total'], 'Memory (MiB)')

    plotter('transient_memory_mpi', LOCATION, 'time', EXT,
            ['normal', 'batch-restore'], ['time'], ['Time'], 'Time (sec.)')

    plotter('transient_memory_mpi', LOCATION, '', EXT,
            ['normal', 'batch-restore'], ['total', 'max_proc'], ['Total', 'Max'], 'Memory (MiB)')
    """
