#!/usr/bin/env python3
import gmsh
import pandas
import math
import numpy
import scipy.interpolate
import enum

import dataclasses

@dataclasses.dataclass
class Node:
    tag: int
    coords: list#[float]

    def __init__(self, *, tag=None, coords=None):
        self.tag = tag
        self.coords = coords


def get_node_tag():
    nodes, coords, pcoords = gmsh.model.mesh.getNodes()
    return nodes[-1] + 1 if nodes.size > 0 else 1


def rectangle():

    n_top = 20
    n_bot = 10

    gmsh.initialize()
    gmsh.model.add('rectangle')

    top_points = [gmsh.model.geo.addPoint(i/n_top, 1, 0, 1/n_top) for i in range(n_top)]
    bot_points = [gmsh.model.geo.addPoint(i/n_bot, 0, 0, 1/n_bot) for i in range(n_bot)]

    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    line_left = gmsh.model.geo.addLine(bot_points[0], top_points[0])

    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surface = gmsh.model.geo.addPlaneSurface([curve])

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)

    gmsh.fltk.run()
    gmsh.finalize()

def get_nodes(file_name, elem_size):
    # Create coordinate grids
    points = pandas.read_csv(file_name)

    xmin = points['x'].min()
    xmax = points['x'].max()
    ymin = points['y'].min()
    ymax = points['y'].max()

    nx = math.ceil((xmax - xmin) / elem_size)
    ny = math.ceil((ymax - ymin) / elem_size)

    xi = numpy.linspace(xmin, xmax, nx)
    yi = numpy.linspace(ymin, ymax, ny)
    grid_x, grid_y = numpy.meshgrid(xi, yi)
    grid_z = scipy.interpolate.griddata((points['x'], points['y']), points['z'], (grid_x, grid_y), method='nearest')


    nid = get_node_tag()
    nodes = numpy.ndarray((nx, ny), dtype=Node)
    for i in range(nx):
        for j in range(ny):
            nodes[i,j] = Node(tag=int(nid), coords=[grid_x[i, j], grid_y[i, j], grid_z[i, j]])
            nid += 1

    return nodes, (xmax-xmin)/nx, (ymax-ymin)/ny

def surface():
    top_nodes, top_xsize, top_ysize = get_nodes('granitoid_40m.csv', 100)
    bot_nodes, bot_xsize, bot_ysize = get_nodes('bottom_40m.csv', 500)

    gmsh.initialize()
    gmsh.model.add('surface')

    top_points = [gmsh.model.geo.addPoint(*top_nodes[0,j].coords, meshSize=100) for j in range(top_nodes.shape[1])]
    bot_points = [gmsh.model.geo.addPoint(*bot_nodes[0,j].coords, meshSize=500) for j in range(bot_nodes.shape[1])]

    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    line_left = gmsh.model.geo.addLine(bot_points[0], top_points[0])

    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surface = gmsh.model.geo.addPlaneSurface([curve])

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.embed(0, top_points, 2, surface)
    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate()

    gmsh.fltk.run()
    gmsh.finalize()

if __name__ == '__main__':
    #rectangle() # works fine
    surface()
