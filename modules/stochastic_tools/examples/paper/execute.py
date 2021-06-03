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

def get_args():
    parser = argparse.ArgumentParser(description='Utility for producing results, plots, and tables for STM paper')
    parser.add_argument('--skip-weak', action='store_true', help="Disable performing stochastic runs for weak scaling.")
    parser.add_argument('--skip-memory', action='store_true', help="Disable performing stochastic runs for memory/timing.")
    parser.add_argument('--replicates', default=10, type=int, help="Number of replicates to perform.")
    parser.add_argument('--base', default=128, type=int, help="The base number of samples to perform.")
    parser.add_argument('--memory-levels', default=6, type=int, help="Number of levels to perform for memory/timing runs, n in [base*2^0, ..., base*2^n-1].")
    parser.add_argument('--memory-cores', default=32, type=int, help="Number of processors to use for memory/timing runs.")
    parser.add_argument('--weak-levels', default=7, type=int, help="Number of processor levels to perform for weak scaling, n in [2^0,...,2^n-1].")

    return parser.parse_args()

def execute(infile, outfile, mode, samples, mpi=None, replicates=1):
    data = collections.defaultdict(list)
    if mpi is None: mpi = [1]*len(samples)
    exe = mooseutils.find_moose_executable_recursive()
    for n_cores, n_samples in zip(mpi, samples):
        cmd = ['mpiexec', '-n', str(n_cores), exe, '-i', infile, 'Samplers/mc/num_rows={}'.format(int(n_samples)),
               'Executioner/num_steps={}'.format(replicates),
               'MultiApps/runner/mode={}'.format(mode),
               'Outputs/file_base={}'.format(mode)]

        print(' '.join(cmd))
        out = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        local = pandas.read_csv('{}.csv'.format(mode))
        data['n_ranks'].append(n_cores)
        data['n_samples'].append(n_samples)
        data['mem_total'].append(local['total'].iloc[1])
        data['mem_per_proc'].append(local['per_proc'].iloc[1])
        data['mem_max_proc'].append(local['max_proc'].iloc[1])
        data['run_time'].append(statistics.mean(local['run_time'].iloc[1:]))
        data['run_time_min'].append(min(local['run_time'].iloc[1:]))
        data['run_time_max'].append(max(local['run_time'].iloc[1:]))

        df = pandas.DataFrame(data, columns=data.keys())
        df.to_csv('results/{}_{}.csv'.format(outfile, mode))


def plot(prefix, suffix, xname, yname, xlabel=None, ylabel=None, xlog=None, ylog=None, yerr=None):

    fig = plt.figure(figsize=[4,4], dpi=300, tight_layout=True)
    ax = fig.subplots()

    for i, mode in enumerate(['normal']):#, 'batch-restore', 'batch-reset']):
        data = pandas.read_csv('results/{}_{}.csv'.format(prefix, mode))
        kwargs = dict()
        kwargs['label'] = mode
        kwargs['markersize'] = 4
        kwargs['marker'] = 'osd'[i]
        if yerr is not None:
            kwargs['capsize'] = 2
            kwargs['yerr'] = [ (data[yerr[0]] - data[yname]).tolist(),
                               (data[yname] - data[yerr[1]]).tolist()]
        ax.errorbar(data[xname], data[yname], **kwargs)

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
            times[key].append((row['run_time'], row['run_time_max'], row['run_time_min']))

    for key, value in times.items():
        n_samples = key[0]
        n_ranks = key[1]
        normal = '{:.1f} ({:.1f}, {:.1f})'.format(*value[0])
        reset = '{:.1f} ({:.1f}, {:.1f})'.format(*value[1])
        restore = '{:.1f} ({:.1f}, {:.1f})'.format(*value[2])
        out.append(r'{} & {} & {} & {} & {} \\'.format(n_ranks, n_samples, normal, reset, restore))

    out.append(r'\bottomrule')
    out.append(r'\end{tabular}')

    with open('weak.tex', 'w') as fid:
        fid.write('\n'.join(out))

if __name__ == '__main__':

    input_file = 'full_solve.i'
    args = get_args()

    # Memory Parallel
    if not args.skip_memory:
        prefix = 'full_solve_memory_parallel'
        samples = [args.base*2**n for n in range(args.memory_levels)]
        mpi = [args.memory_cores]*len(samples)
        execute(input_file, prefix, 'normal', samples, mpi, args.replicates)
        execute(input_file, prefix, 'batch-reset', samples, mpi, args.replicates)
        execute(input_file, prefix, 'batch-restore', samples, mpi, args.replicates)

    # Weak scale
    if not args.skip_weak:
        prefix = 'full_solve_weak_scale'
        mpi = [2**n for n in range(args.weak_levels)]
        samples = [args.base*m for m in mpi]
        execute(input_file, prefix, 'normal', samples, mpi, args.replicates)
        execute(input_file, prefix, 'batch-reset', samples, mpi, args.replicates)
        execute(input_file, prefix, 'batch-restore', samples, mpi, args.replicates)

    # Parallel time and memory plots
    plot('full_solve_memory_parallel', 'time',
         xname='n_samples', xlabel='Number of Simulations', xlog=None,
         yname='run_time', ylabel='Time (sec.)', yerr=('run_time_min', 'run_time_max'), ylog=None)

    plot('full_solve_memory_parallel', 'memory',
         xname='n_samples', xlabel='Number of Simulations', xlog=None,
         yname='mem_per_proc', ylabel='Memory (MiB)', ylog=None)

    # Weak scaling table
    table('full_solve_weak_scale')
