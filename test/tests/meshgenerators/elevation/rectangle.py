#!/usr/bin/env python3
import gmsh
import math


def surface():
    """This works like I would expect with element vertex at points"""
    n_top = 20
    n_bot = 10

    gmsh.initialize()
    gmsh.model.add('surface')

    top_y_func = lambda x: 1 + 0.1*math.sin(math.pi*x)
    top_points = [gmsh.model.geo.addPoint(i/n_top, top_y_func(i/n_top), 0, 1/(n_top-1)) for i in range(n_top+1)]
    #top_points = [gmsh.model.geo.addPoint(i/n_top, top_y_func(i/n_top), 0, 1/(n_top+1)) for i in range(n_top+1)]
    #top_points = [gmsh.model.geo.addPoint(i/n_top, top_y_func(i/n_top), 0, 1/n_top) for i in range(n_top+1)]
    bot_points = [gmsh.model.geo.addPoint(i/n_bot, 0, 0, 1/n_bot) for i in range(n_bot+1)]

    line_top = gmsh.model.geo.addPolyline(top_points)
    line_bot = gmsh.model.geo.addPolyline(bot_points)
    line_right = gmsh.model.geo.addLine(bot_points[-1], top_points[-1])
    line_left = gmsh.model.geo.addLine(bot_points[0], top_points[0])

    curve = gmsh.model.geo.addCurveLoop([line_top, -line_right, -line_bot, line_left])
    surface = gmsh.model.geo.addPlaneSurface([curve])

    gmsh.model.geo.synchronize()

    #https://gitlab.onelab.info/gmsh/gmsh/blob/gmsh_4_8_4/tutorial/python/t15.py#L47
    gmsh.model.mesh.embed(0, top_points, 2, surface) # this does nothing
    gmsh.model.mesh.generate()

    gmsh.fltk.run()
    gmsh.finalize()

if __name__ == '__main__':
    surface()
