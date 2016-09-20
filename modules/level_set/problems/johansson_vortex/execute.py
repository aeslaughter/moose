#!/usr/bin/env python
import sys
import os
import argparse
import re
import subprocess

parser = argparse.ArgumentParser(description='Script for running the vortex problem.')
parser.add_argument('input', type=str, help='Input file name to run.')
parser.add_argument('-n', '--parallel', default='1', type=str, help='Number of MPI postprocessors.')
parser.add_argument('-j', '--n-threads', default='1', type=str, help='Number of theads.')
parser.add_argument('--dry', action='store_true', help='Just print the command')

parser.add_argument('--mesh', default='64', type=str, help='The number of mesh elements in x and y direction.')
parser.add_argument('--scheme', default='implicit-euler', type=str, help='The time integration scheme.')
parser.add_argument('--dt', default='0.5*cfl', type=str, help="The time step size (number or 'x*cfl')")
parser.add_argument('--elem', default='QUAD4', type=str, help="The element type to mesh.")
parser.add_argument('--order', default='FIRST', type=str, help="The variable order to solve.")

args = parser.parse_args()
cli_args = []
cli_args += ['Mesh/nx=' + args.mesh, 'Mesh/ny=' + args.mesh]
cli_args += ['Mesh/elem_type=' + args.elem]
cli_args += ['Variables/phi/order=' + args.order]
cli_args += ['Executioner/scheme=' + args.scheme]

# Timestep
try:
    dt = float(args.dt)
    cli_args += ['Executioner/TimeStepper/postprocessor=' + args.dt]
except:
    match = re.search(r'(\d*\.\d*|\d*)\*cfl', args.dt)
    if not match:
        print "Failed to determine CFL based timestep, must use 'x*cfl'"
        sys.exit()
    cli_args += ['Executioner/TimeStepper/postprocessor=cfl', 'Executioner/TimeStepper/scale=' + str(match.group(1))]

# file_base
d = vars(args)
keys = ['mesh', 'scheme', 'dt', 'elem', 'order']
fb = []
for k in keys:
    fb.append(k + '=' + d[k])
name, ext = os.path.splitext(args.input)
file_base = name + '_(' + '_'.join(fb) + ')'
file_base = file_base.replace('*','')

cli_args += ['Outputs/file_base=' + file_base]


opt = os.path.join(os.environ['MOOSE_DIR'], 'modules', 'level_set', 'level_set-opt')
cmd = ['mpiexec', '-n', args.parallel, opt, '-i', args.input, '--n-threads=' + args.n_threads]
cmd += cli_args

print ' '.join(cmd)
if not args.dry:
    subprocess.call(cmd)
