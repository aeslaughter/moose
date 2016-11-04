#!/usr/bin/env python
import vtk
import chigger
import math
import pandas
import argparse
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

def get_options():
    parser = argparse.ArgumentParser(description="Process results for initial/final condition and/or area conservation.")
    parser.add_argument('-e', '--exodus', nargs='*', help="The ExodusII files to process.")
    parser.add_argument('-a', '--area', nargs='*', help="The CSV files to process.")

    return parser.parse_args()

def exodus(filenames):
    """
    Process exodus files expressed as a glob pattern for beginning end contours.

    Args:
        filenames[list]: A list of filenames to open.
    """

    # Get the list of filenames
    colors = cm.Accent(np.linspace(0, 1, len(filenames)))

    # Shared camera from variable and contour
    camera = vtk.vtkCamera()
    camera.SetViewUp(0.0000, 1.0000, 0.0000)
    camera.SetPosition(0.0000, 0.5000, 0.6773)
    camera.SetFocalPoint(0.0000, 0.5000, 0.0000)

    def get_result(filename, levels=[], timestep=-1, color=[0,0,0], **kwargs):
        reader = chigger.ExodusReader(filename, timestep=timestep)
        result = chigger.ExodusResult(reader, color=color, camera=camera, variable='phi', range=[0, 1], **kwargs)# viewport=[0,0,0.5,1])
        result.SetOptions('colorbar', visible=False)
        if levels:
            result.SetOptions('contour', visible=True, levels=levels)
        return result


    # Initial Condition
    results = []
    #results.append(get_result(filenames[-1], opacitiy=0.5, cmap='viridis',
    #                          extents={'visible':True, 'xaxis':{'color':[0,0,0]}, 'yaxis':{'color':[0,0,0]}}))
    results.append(get_result(filenames[-1], levels=[0.5], timestep=0, color=[0,0,0]))

    # Add results
    for filename, color in zip(filenames, colors):
        results.append(get_result(filename, levels=[0.5], color=list(color[:3])))

    window = chigger.RenderWindow(*results, background=[1,1,1], size=[400,400], style='interactive2D')
    window.Write('output.png')
    window.Start()
    results[0].PrintCamera()

def area(filenames):
    """
    Process the area plots for supplied csv files.
    """

    fig = plt.figure(facecolor=[1,1,1])
    ax = plt.subplot(111)

    for filename in filenames:
        data = pandas.read_csv(filename)
        ax.plot(data['time'], data['area'])

    a = math.pi*0.15**2
    t = [data['time'].iloc[0], data['time'].iloc[-1]]
    ax.plot(t, [a,a], '-k')

    plt.show()



if __name__ == '__main__':


    # Parse command line
    opt = get_options()

    # Exodus
    if opt.exodus:
        exodus(opt.exodus)
    if opt.area:
        area(opt.area)
