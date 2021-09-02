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
import dataclasses

class ElementType(enum.IntEnum):
    POINT = 15
    LINE2 = 1
    TRI3 = 2
    QUAD4 = 3


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

    # Create 4 discrete points for the 4 corners of the terrain surface
    pt0 = gmsh.model.addDiscreteEntity(0)
    gmsh.model.setCoordinates(pt0, *nodes[0,0].coords)

    pt1 = gmsh.model.addDiscreteEntity(0)
    gmsh.model.setCoordinates(pt1, *nodes[0,-1].coords)

    pt2 = gmsh.model.addDiscreteEntity(0)
    gmsh.model.setCoordinates(pt2, *nodes[-1,-1].coords)

    pt3 = gmsh.model.addDiscreteEntity(0)
    gmsh.model.setCoordinates(pt3, *nodes[-1,0].coords)

    # Create 4 discrete bounding curves, with their boundary points:
    bnd0 = gmsh.model.addDiscreteEntity(1, boundary=[pt0, pt1])
    bnd1 = gmsh.model.addDiscreteEntity(1, boundary=[pt1, pt2])
    bnd2 = gmsh.model.addDiscreteEntity(1, boundary=[pt2, pt3])
    bnd3 = gmsh.model.addDiscreteEntity(1, boundary=[pt3, pt0])

    # Create one discrete surface, with its bounding curves:
    surface = gmsh.model.addDiscreteEntity(2, boundary=[bnd0, bnd1, bnd2, bnd3])

    gmsh.model.mesh.addNodes(2, surface, [n.tag for n in nodes.flat],
                             list(itertools.chain.from_iterable(n.coords for n in nodes.flat)))


    # Mesh corners
    gmsh.model.mesh.addElementsByType(pt0, ElementType.POINT, [], [nodes[0,0].tag])
    gmsh.model.mesh.addElementsByType(pt1, ElementType.POINT, [], [nodes[0,-1].tag])
    gmsh.model.mesh.addElementsByType(pt2, ElementType.POINT, [], [nodes[-1,-1].tag])
    gmsh.model.mesh.addElementsByType(pt3, ElementType.POINT, [], [nodes[-1,0].tag])

    gmsh.model.mesh.addElementsByType(bnd0, ElementType.LINE2, [], [nodes[0,0].tag, nodes[0,-1].tag])
    gmsh.model.mesh.addElementsByType(bnd1, ElementType.LINE2, [], [nodes[0,-1].tag, nodes[-1,-1].tag])
    gmsh.model.mesh.addElementsByType(bnd2, ElementType.LINE2, [], [nodes[-1,-1].tag, nodes[-1,0].tag])
    gmsh.model.mesh.addElementsByType(bnd3, ElementType.LINE2, [], [nodes[-1,0].tag, nodes[0,0].tag])



    elements = []
    for i in range(nx-1):
        for j in range(ny-1):
            elements += [nodes[i,j].tag, nodes[i+1, j].tag, nodes[i+1,j+1].tag]
            elements += [nodes[i,j].tag, nodes[i+1, j+1].tag, nodes[i,j+1].tag]

    gmsh.model.mesh.addElementsByType(surface, ElementType.TRI3, [], elements)
    #print(gmsh.model.getEntities(2))
    #print(gmsh.model.getEntities(1))
    #gmsh.model.mesh.reclassifyNodes()
    gmsh.model.mesh.createGeometry()
    #print(gmsh.model.getEntities(2))
    #print(gmsh.model.getEntities(1))



    return nodes, surface



def build_sides(bot_nodes, top_nodes, bot_elem_size=0, top_elem_size=0):

    surfaces = list()


    # X=0 face: i=0, j
    top_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=top_elem_size) for n in top_nodes[0,:]]
    bot_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=bot_elem_size) for n in bot_nodes[0,:]]
    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[0], top_points[0])
    line_left = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # X=-1 face: i=-1, j
    top_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=top_elem_size) for n in top_nodes[-1,:]]
    bot_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=bot_elem_size) for n in bot_nodes[-1,:]]
    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[0], top_points[0])
    line_left = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    #curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=0 face: i, j=0
    top_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=top_elem_size) for n in top_nodes[:,0]]
    bot_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=bot_elem_size) for n in bot_nodes[:,0]]
    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[0], top_points[0])
    line_left = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])

#    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=-1 face: i, j=01
    top_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=top_elem_size) for n in top_nodes[:,-1]]
    bot_points = [gmsh.model.geo.addPoint(*n.coords, meshSize=bot_elem_size) for n in bot_nodes[:,-1]]
    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[0], top_points[0])
    line_left = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])

    #curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))


    return surfaces


def main():
    gmsh.initialize()
    gmsh.model.add('simple')

    bot_nodes, bot_surface = build_surface('bottom_40m.csv', 500)
    mid_nodes, mid_surface = build_surface('granitoid_40m.csv', 100)
    top_nodes, top_surface = build_surface('surface_40m.csv', 100)

    surfaces = [bot_surface, mid_surface, top_surface]

    #surfaces += build_sides(bot_nodes, mid_nodes, 500, 100)
    #surfaces += build_sides(mid_nodes, top_nodes)

    #faces = gmsh.model.geo.addSurfaceLoop(surfaces)
    #volume = gmsh.model.geo.addVolume([faces])

    #gmsh.option.setNumber("General.Verbosity", 99)
    #gmsh.option.setNumber("Coherence.Mesh", 1)
    #gmsh.option.setNumber("Geometry.AutoCoherence", 2)

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)

    #gmsh.write("simple.msh")
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == '__main__':
    main()
