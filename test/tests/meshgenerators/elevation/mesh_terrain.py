#!/usr/bin/env python3
import gmsh
import pandas
import math
import numpy
import scipy.interpolate
import dataclasses

def get_nodes(file_name: str, elem_size: int) -> numpy.ndarray:
    """
    Compute the coordinates from XYZ data on a regular grid.

    The *file_name* should be a CSV data, with headings of 'x', 'y', and 'z' that defines a
    terrain surface. The data is sampled onto a regular grid with spacing approximatly equal to
    the supplied *elem_size*.
    """
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

    nodes = numpy.ndarray((nx, ny), dtype=tuple)
    for i in range(nx):
        for j in range(ny):
            nodes[i,j] = (grid_x[i, j], grid_y[i, j], grid_z[i, j])

    return nodes

def build_surface(file_name, elem_size):

    nodes = get_nodes(file_name, elem_size)

    nx, ny = nodes.shape
    points = numpy.ndarray((nx, ny), dtype=int)
    for i in range(nx):
        for j in range(ny):
            points[i,j] = gmsh.model.occ.addPoint(*nodes[i,j], meshSize=elem_size)


    surface = gmsh.model.occ.addBSplineSurface(list(points.flatten()), nx)
    gmsh.model.occ.synchronize()

    boundaries = gmsh.model.getBoundary([(2, surface)])
    return surface, [b[1] for b in boundaries], points

def build_sides(bot_lines, bot_points, top_lines, top_points):

    surfaces = list()
    vert_lines = [gmsh.model.occ.addLine(bot_points[-1,0], top_points[-1,0]),
                  gmsh.model.occ.addLine(bot_points[0,0], top_points[0,0]),
                  gmsh.model.occ.addLine(bot_points[0,-1], top_points[0,-1]),
                  gmsh.model.occ.addLine(bot_points[-1,-1], top_points[-1,-1])]

    # YZ-plane at X=0
    curve = gmsh.model.occ.addCurveLoop([vert_lines[0], top_lines[0], -vert_lines[1], -bot_lines[0]])
    surfaces.append(gmsh.model.occ.addPlaneSurface([curve]))

    # XZ-plane at Y=0
    curve = gmsh.model.occ.addCurveLoop([vert_lines[1], top_lines[1], -vert_lines[2], -bot_lines[1]])
    surfaces.append(gmsh.model.occ.addPlaneSurface([curve]))

    # YZ-plane at X=-1
    curve = gmsh.model.occ.addCurveLoop([vert_lines[2], top_lines[2], -vert_lines[3], -bot_lines[2]])
    surfaces.append(gmsh.model.occ.addPlaneSurface([curve]))

    # XZ-plane at Y=-1
    curve = gmsh.model.occ.addCurveLoop([vert_lines[3], top_lines[3], -vert_lines[0], -bot_lines[3]])
    surfaces.append(gmsh.model.occ.addPlaneSurface([curve]))

    gmsh.model.occ.synchronize()
    return surfaces


def main():
    gmsh.initialize()
    gmsh.model.add('terrain')

    #top_surface, top_bounds, top_points = build_surface('surface_40m.csv', 100)
    mid_surface, mid_bounds, mid_points = build_surface('granitoid_40m.csv', 100)
    bot_surface, bot_bounds, bot_points = build_surface('bottom_40m.csv', 100)

    #surfaces = build_sides(mid_bounds, mid_points, top_bounds, top_points)
    surfaces = build_sides(bot_bounds, bot_points, mid_bounds, mid_points)
    surfaces += [mid_surface, bot_surface]

    faces = gmsh.model.occ.addSurfaceLoop(surfaces)
    volume = gmsh.model.occ.addVolume([faces])
    gmsh.model.occ.synchronize()




    gmsh.model.mesh.generate()


    gmsh.fltk.run()
    gmsh.finalize()

if __name__ == '__main__':
    main()
