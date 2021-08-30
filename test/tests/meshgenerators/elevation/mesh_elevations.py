#!/usr/bin/env python3
import gmsh
import sys
import pandas
import math
import numpy
import scipy.interpolate

def build_surface(file_name, elem_size):

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

    # Build points and surfaces
    nid = 1
    points = numpy.ndarray((nx, ny), dtype=int)
    for i in range(nx):
        for j in range(ny):
            points[i,j] = gmsh.model.geo.addPoint(grid_x[i, j], grid_y[i, j], grid_z[i, j], elem_size)

    compound = list()
    for i in range(nx - 1):
        for j in range(ny - 1):
            lines = list()
            lines.append(gmsh.model.geo.addLine(points[i,j], points[i+1,j]))
            lines.append(gmsh.model.geo.addLine(points[i+1,j], points[i+1,j+1]))
            lines.append(gmsh.model.geo.addLine(points[i+1,j+1], points[i,j+1]))
            lines.append(gmsh.model.geo.addLine(points[i,j+1], points[i,j]))

            curve = gmsh.model.geo.addCurveLoop(lines)
            #compound.append(gmsh.model.geo.addSurfaceFilling([curve]))
            compound.append(gmsh.model.geo.addPlaneSurface([curve]))

    surface = gmsh.model.geo.addSurfaceLoop(compound)

    return points, surface

def build_volume(bot_points, top_points):

    surfaces = list()

    # X=0 face: i=0, j
    line_top = gmsh.model.geo.addPolyline(top_points[0,:])
    line_bot = gmsh.model.geo.addPolyline(bot_points[0,:])
    line_right = gmsh.model.geo.addLine(bot_points[0,0], top_points[0,0])
    line_left = gmsh.model.geo.addLine(bot_points[0,-1], top_points[0,-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # X=-1 face: i=-1, j
    line_top = gmsh.model.geo.addPolyline(top_points[-1,:])
    line_bot = gmsh.model.geo.addPolyline(bot_points[-1,:])
    line_right = gmsh.model.geo.addLine(bot_points[-1,-1], top_points[-1,-1])
    line_left = gmsh.model.geo.addLine(bot_points[-1,0], top_points[-1,0])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=0 face: i, j=0
    line_top = gmsh.model.geo.addPolyline(top_points[:,0])
    line_bot = gmsh.model.geo.addPolyline(bot_points[:,0])
    line_right = gmsh.model.geo.addLine(bot_points[-1,0], top_points[-1,0])
    line_left = gmsh.model.geo.addLine(bot_points[0,0], top_points[0,0])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    # Y=-1 face: i, j=01
    line_top = gmsh.model.geo.addPolyline(top_points[:,-1])
    line_bot = gmsh.model.geo.addPolyline(bot_points[:,-1])
    line_right = gmsh.model.geo.addLine(bot_points[0,-1], top_points[0,-1])
    line_left = gmsh.model.geo.addLine(bot_points[-1,-1], top_points[-1,-1])
    curve = gmsh.model.geo.addCurveLoop([line_top, -line_left, -line_bot, line_right])
    surfaces.append(gmsh.model.geo.addPlaneSurface([curve]))

    return surfaces


def main():
    gmsh.initialize()
    gmsh.model.add('simple')

    bot_points, bot_surface = build_surface('bottom_40m.csv', 500)
    mid_points, mid_surface = build_surface('granitoid_40m.csv', 100)
    top_points, top_surface = build_surface('surface_40m.csv', 100)

    surfaces = [bot_surface, mid_surface, top_surface]

    surfaces += build_volume(bot_points, mid_points)
    surfaces += build_volume(mid_points, top_points)

    faces = gmsh.model.geo.addSurfaceLoop(surfaces)
    volume = gmsh.model.geo.addVolume([faces])
    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate(3)

    gmsh.write("simple.msh")
    gmsh.fltk.run()
    gmsh.finalize()


if __name__ == '__main__':
    main()
