#!/usr/bin/env python3
import gmsh
import math


def surface():
    """This works like I would expect with element vertex at points"""
    n_top = 10
    n_mid = 20
    n_bot = 10

    gmsh.initialize()
    gmsh.model.add('surface')

    mid_y_func = lambda x: 1 + 0.1*math.sin(math.pi*x)

    top_points = [gmsh.model.geo.addPoint(i/n_top, 2, 0, 1/n_top) for i in range(n_top+1)]
    mid_points = [gmsh.model.geo.addPoint(i/n_top, mid_y_func(i/n_top), 0, 1/n_top) for i in range(n_mid+1)]
    bot_points = [gmsh.model.geo.addPoint(i/n_bot, 0, 0, 1/n_bot) for i in range(n_bot+1)]




    """
    lines = []
    for i in range(n_top):
        lines.append(gmsh.model.geo.addLine(top_points[i], top_points[i+1]))
    lines.append(gmsh.model.geo.addLine(top_points[-1], bot_points[-1]))

    for i in range(n_bot, 0, -1):
        lines.append(gmsh.model.geo.addLine(bot_points[i], bot_points[i-1]))

    lines.append(gmsh.model.geo.addLine(bot_points[0], top_points[0]))
    """

    curve = gmsh.model.geo.addCurveLoop(lines)
    surface = gmsh.model.geo.addPlaneSurface([curve])

    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate()

    gmsh.fltk.run()
    gmsh.finalize()

if __name__ == '__main__':
    surface()
