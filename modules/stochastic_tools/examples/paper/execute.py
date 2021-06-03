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
import statistics
import collections
import mooseutils

def execute(infile, outfile, mode, samples, mpi=None, replicates=1):
    data = dict(n_samples=[], n_ranks=[], mem_total=[], mem_per_proc=[], mem_max_proc=[],
                run_time=[], run_time_min=[], run_time_max=[], real_time=[])

    if mpi is None: mpi = [1]*len(samples)
    exe = mooseutils.find_moose_executable_recursive()
    for n_cores, n_samples in zip(mpi, samples):
        cmd = ['mpiexec', '-n', str(n_cores), exe, '-i', infile, 'Samplers/mc/num_rows={}'.format(int(n_samples)),
               'Executioner/num_steps={}'.format(replicates),
               'MultiApps/runner/mode={}'.format(mode),
               'Outputs/file_base={}'.format(mode)]

        print(' '.join(cmd))
        t = time.time()
        out = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t = time.time() - t

        local = pandas.read_csv('{}.csv'.format(mode))
        data['n_ranks'].append(n_cores)
        data['n_samples'].append(n_samples)
        data['mem_total'].append(local['total'].iloc[1])
        data['mem_per_proc'].append(local['per_proc'].iloc[1])
        data['mem_max_proc'].append(local['max_proc'].iloc[1])
        data['run_time'].append(statistics.mean(local['run_time'].iloc[1:]))
        data['run_time_min'].append(min(local['run_time'].iloc[1:]))
        data['run_time_max'].append(max(local['run_time'].iloc[1:]))
        data['real_time'].append(t)

        df = pandas.DataFrame(data, columns=data.keys())
        df.to_csv('results/{}_{}.csv'.format(outfile, mode))


def plot(prefix, suffix, xname, yname, xlabel=None, ylabel=None, xlog=None, ylog=None):

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

def table(prefix):

    out = list()
    out.append(r'\begin{tabular}{ccccc}')
    out.append(r'\toprule')
    out.append(r'& & {} \\'.format('\multicolumn{3}{c}{time (sec.)}'))
    out.append(r'\cmidrule{3-5}')
    out.append(r'{} & {} & {} & {} & {} \\'.format('Processors', 'Simulations', 'normal', 'batch-reset', 'batch-restore'))
    out.append(r'\midrule')

    times = collections.defaultdict(list)
    for i, mode in enumerate(['normal', 'batch-reset', 'batch-restore']):
        data = pandas.read_csv('results/{}_{}.csv'.format(prefix, mode))
        for idx, row in data.iterrows():
            key = (int(row['n_samples']), int(row['n_ranks']))
            times[key].append((row['run_time'], row['run_time_min'], row['run_time_max']))

    for key, value in times.items():
        n_samples = key[0]
        n_ranks = key[1]
        normal = '{:.1f} ({:.1f}, {:.1f})'.format(*value[0])
        reset = '{:.1f} ({:.1f}, {:.1f})'.format(*value[1])
        restore = '{:.1f} ({:.1f}, {:.1f})'.format(*value[2])
        out.append(r'{} & {} & {} & {} & {} \\'.format(n_ranks, n_samples, normal, reset, restore))

    out.append('\bottomrule')
    out.append('\end{tabular}')
    print('\n'.join(out))

if __name__ == '__main__':

    input_file = 'full_solve.i'
    base = 2
    replicates = 5

    # Memory Parallel
    if False:
        prefix = 'full_solve_memory_parallel'
        samples = [base, base*2]
        #samples = [base, base*2, base*4, base*8, base*16, base*32]
        mpi = [32]*len(samples)
        execute(input_file, prefix, 'normal', samples, mpi, replicates)
        execute(input_file, prefix, 'batch-reset', samples, mpi, replicates)
        execute(input_file, prefix, 'batch-restore', samples, mpi, replicates)

    # Weak scale
    if False:
        prefix = 'full_solve_weak_scale'
        #mpi = [1, 2, 4, 8, 16, 32, 64]
        mpi = [1, 2]
        samples = [base*m for m in mpi]
        execute(input_file, prefix, 'normal', samples, mpi, replicates)
        execute(input_file, prefix, 'batch-reset', samples, mpi, replicates)
        execute(input_file, prefix, 'batch-restore', samples, mpi, replicates)


    # Parallel time and memory plots
    plot('full_solve_memory_parallel', 'time',
         xname='n_samples', xlabel='Number of Simulations', xlog=None,
         yname='run_time', ylabel='Time (sec.)', ylog=None)

    plot('full_solve_memory_parallel', 'memory',
         xname='n_samples', xlabel='Number of Simulations', xlog=None,
         yname='mem_per_proc', ylabel='Memory (MiB)', ylog=None)

    table('full_solve_weak_scale')
