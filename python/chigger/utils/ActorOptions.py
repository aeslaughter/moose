import vtk
from .Options import Options

def validOptions(actor_type=vtk.vtkActor):
    """Returns options for edge properties for vtkActor objects."""
    opt = Options()
    opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
    opt.add('color', vtype=(float, int), size=3, doc="The color of the object.")
    opt.add('linewidth', 1, vtype=(int, float), doc="The line width for the object.")

    opt.add('representation', default='surface', allow=('surface', 'wireframe', 'points'),
            doc="View volume representation.")

    opt.add('edges', default=False, vtype=bool,
            doc="Enable edges on the rendered object.")
    opt.add('edgecolor', default=(0.5,)*3, array=True, size=3, vtype=float,
            doc="The color of the edges, 'edges=True' must be set.")
    opt.add('edgewidth', default=1, vtype=(float, int),
            doc="The width of the edges, 'edges=True' must be set.")

    opt.add('lines_as_tubes', default=False, vtype=bool,
            doc="Toggle rendering 1D lines as tubes.")

    opt.add('pointsize', default=1, vtype=(float, int),
            doc="The point size to utilized.")

    return opt

def applyOptions(vtkactor, opt):
    opt.assign('color', vtkactor.GetProperty().SetColor)
    opt.assign('opacity', vtkactor.GetProperty().SetOpacity)
    opt.assign('linewidth', vtkactor.GetProperty().SetLineWidth)

    if isinstance(vtkactor, vtk.vtkActor):
        rep = opt.get('representation')
        if rep == 'surface':
            vtkactor.GetProperty().SetRepresentationToSurface()
        elif rep == 'wireframe':
            vtkactor.GetProperty().SetRepresentationToWireframe()
        elif rep == 'points':
            vtkactor.GetProperty().SetRepresentationToPoints()

    opt.assign('edges', vtkactor.GetProperty().SetEdgeVisibility)
    opt.assign('edgecolor', vtkactor.GetProperty().SetEdgeColor)
    opt.assign('edgewidth', vtkactor.GetProperty().SetLineWidth)

    opt.assign('lines_as_tubes', vtkactor.GetProperty().SetRenderLinesAsTubes)

    opt.assign('pointsize', vtkactor.GetProperty().SetPointSize)

    opt.assign('opacity', vtkactor.GetProperty().SetOpacity)
