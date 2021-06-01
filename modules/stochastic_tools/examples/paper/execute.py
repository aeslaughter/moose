#!/usr/bin/env python3
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

import subprocess
import time
import argparse
import pandas
import matplotlib.pyplot as plt
import multiprocessing
import mooseutils

def execute(infile, outfile, mode, samples, mpi=None):
    data = dict(n_samples=[], n_ranks=[], total=[], per_proc=[], max_proc=[], time=[])

    if mpi is None: mpi = [1]*len(samples)
    exe = mooseutils.find_moose_executable_recursive()
    for n_cores, n_samples in zip(mpi, samples):
        cmd = ['mpiexec', '-n', str(n_cores), exe, '-i', infile, 'Samplers/mc/num_rows={}'.format(int(n_samples)),
               'MultiApps/runner/mode={}'.format(mode),
               'Outputs/file_base={}'.format(mode)]

        print(' '.join(cmd))
        t = time.time()
        out = subprocess.run(cmd, text=True, capture_output=True)
        t = time.time() - t

        local = pandas.read_csv('{}.csv'.format(mode))
        data['n_ranks'].append(n_cores)
        data['n_samples'].append(n_samples)
        data['total'].append(local['total'].iloc[-1])
        data['per_proc'].append(local['per_proc'].iloc[-1])
        data['max_proc'].append(local['max_proc'].iloc[-1])
        data['time'].append(t)

        df = pandas.DataFrame(data, columns=['n_samples', 'n_ranks', 'total', 'per_proc', 'max_proc', 'time'])
        df.to_csv('results/{}_{}.csv'.format(outfile, mode), index=False)

if __name__ == '__main__':
    """
    Mac Pro (2019)
    2.5 GHz 28-Core Intel Xeon W
    240 GB 2933 MHz DDR4
    """
    # Memory Serial
    input_file = 'full_solve.i'
    if False:
        prefix = 'full_solve_memory_serial'
        samples = [1e1, 1e2, 1e3, 1e4, 1e5]
        execute(input_file, prefix , 'normal', samples)
        execute(input_file, prefix, 'batch-reset', samples)
        execute(input_file, prefix, 'batch-restore', samples)

    # Memory Parallel
    if False:
        prefix = 'full_solve_memory_parallel'
        samples = [1e1, 1e2, 1e3, 1e4, 1e5]
        mpi = [24]*len(samples)
        execute(input_file, prefix, 'normal', samples, mpi)
        execute(input_file, prefix, 'batch-reset', samples, mpi)
        execute(input_file, prefix, 'batch-restore', samples, mpi)

    # Strong scale
    if True:
        prefix = 'full_solve_strong_scale'
        mpi = [1, 2, 4, 8, 16, 32]
        samples = [1e3]*len(mpi)
        execute(input_file, prefix, 'normal', samples, mpi)
        execute(input_file, prefix, 'batch-reset', samples, mpi)
        execute(input_file, prefix, 'batch-restore', samples, mpi)

    # Weak scale
    if True:
        prefix = 'full_solve_weak_scale'
        mpi = [1, 2, 4, 8, 16, 32]
        samples = [1e3, 2e3, 4e3, 8e3, 16e3, 32e3]
        execute(input_file, prefix, 'normal', samples, mpi)
        execute(input_file, prefix, 'batch-reset', samples, mpi)
        execute(input_file, prefix, 'batch-restore', samples, mpi)
