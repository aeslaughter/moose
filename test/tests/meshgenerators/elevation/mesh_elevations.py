#!/usr/bin/env python3
import gmsh
import sys
import pandas
import math
import numpy
import scipy.interpolate
import collections
import enum
import itertools
from dataclasses import dataclass

class ElementType(enum.IntEnum):
    POINT = 0
    LINE2 = 1
    TRI3 = 2
    QUAD4 = 3


@dataclass
class Node:
    tag: int
    coords: list#[float]

    def __init__(self, *, tag=None, coords=None):
        self.tag = tag
        self.coords = coords


def get_node_tag():
    nodes, coords, pcoords = gmsh.model.mesh.getNodes()
    return nodes[-1] + 1 if nodes.size > 0 else 1


def build_surface(file_name, elem_size, elem_type=ElementType.TRI3):

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

    elements = []
    for i in range(nx-1):
        for j in range(ny-1):
            elements += [nodes[i,j].tag, nodes[i+1, j].tag, nodes[i+1,j+1].tag]
            elements += [nodes[i,j].tag, nodes[i+1, j+1].tag, nodes[i,j+1].tag]

    surface = gmsh.model.addDiscreteEntity(2)

    gmsh.model.mesh.addNodes(2, surface, [],
                             list(itertools.chain.from_iterable(n.coords for n in nodes.flat)))

    # 2 -> Triangle
    gmsh.model.mesh.addElementsByType(surface, ElementType.TRI3, [], elements)
    return nodes, surface



def build_sides(bot_nodes, top_nodes, bot_elem_size=0, top_elem_size=0):

    surfaces = list()


    top_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=top_elem_size) for n in top_nodes[0,:]]
    bot_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=bot_elem_size) for n in bot_nodes[0,:]]

    # X=0 face: i=0, j
    #surface = gmsh.model.addDiscreteEntity(2)
    #gmsh.model.mesh.addNodes(2, surface, [],
    #                         list(itertools.chain.from_iterable(n.coords for n in top_nodes[0,:].flat)))
    #gmsh.model.mesh.addNodes(2, surface, [],
    #                         list(itertools.chain.from_iterable(n.coords for n in bot_nodes[0,:].flat)))



    #elements = list()
    #for j in range(top_nodes.shape[1] - 1):
    #    elements += [top_nodes[0,j].tag, top_nodes[0,j+1].tag]



    #gmsh.model.mesh.addElementsByType(surface, ElementType.LINE2, [], elements)
    #surfaces.append(surface)


    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[0], top_points[0])
    line_left = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    #gmsh.model.geo.synchronize()

    #gmsh.model.mesh.embed(0, bot_points, 2, surfaces[-1])
    #gmsh.model.mesh.embed(0, top_points, 2, surfaces[-1])

    """
    # X=-1 face: i=-1, j
    line_top = gmsh.model.geo.addPolyline(top_nodes[-1,:].tag)
    line_bot = gmsh.model.geo.addPolyline(bot_nodes[-1,:].tag)
    line_right = gmsh.model.geo.addLine(bot_nodes[-1,-1].tag, top_nodes[-1,-1].tag)
    line_left = gmsh.model.geo.addLine(bot_nodes[-1,0].tag, top_nodes[-1,0].tag)
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=0 face: i, j=0
    line_top = gmsh.model.geo.addPolyline(top_nodes[:,0].tag)
    line_bot = gmsh.model.geo.addPolyline(bot_nodes[:,0].tag)
    line_right = gmsh.model.geo.addLine(bot_nodes[-1,0].tag, top_nodes[-1,0].tag)
    line_left = gmsh.model.geo.addLine(bot_nodes[0,0].tag, top_nodes[0,0].tag)
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=-1 face: i, j=01
    line_top = gmsh.model.geo.addPolyline(top_nodes[:,-1].tag)
    line_bot = gmsh.model.geo.addPolyline(bot_nodes[:,-1].tag)
    line_right = gmsh.model.geo.addLine(bot_nodes[0,-1].tag, top_nodes[0,-1].tag)
    line_left = gmsh.model.geo.addLine(bot_nodes[-1,-1].tag, top_nodes[-1,-1].tag)
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))
    """


    return surfaces


def main():
    gmsh.initialize()
    gmsh.model.add('simple')

    bot_nodes, bot_surface = build_surface('bottom_40m.csv', 500)
    mid_nodes, mid_surface = build_surface('granitoid_40m.csv', 100)
    top_nodes, top_surface = build_surface('surface_40m.csv', 100)

    surfaces = [bot_surface, mid_surface, top_surface]

    surfaces += build_sides(bot_nodes, mid_nodes, 500, 100)
    #surfaces += build_sides(mid_nodes, top_nodes)

    #faces = gmsh.model.geo.addSurfaceLoop(surfaces)
    #volume = gmsh.model.geo.addVolume([faces])

    #gmsh.option.setNumber("General.Verbosity", 99)
    #gmsh.option.setNumber("Coherence.Mesh", 1)
    #gmsh.option.setNumber("Geometry.AutoCoherence", 2)

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)

    gmsh.write("simple.msh")
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == '__main__':
    main()
