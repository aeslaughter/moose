from .Options import Options

def validOptions():
    """Returns options for edge properties for vtkActor objects."""
    opt = Options()

    opt.add('orientation', vtype=(int, float), size=3, doc="The orientation of the object.")
    opt.add('rotation', default=(0., 0., 0.), vtype=(int, float), size=3,
            doc="The rotation of the object about x, y, z axes.")
    opt.add('visible', default=False, doc="Enable/disable display of object edges.")
    opt.add('color', default=(1., 1., 1.), size=3, doc="Set the edge color.")
    opt.add('width', default=1, vtype=int, doc="The edge width, if None then no edges are shown.")
    opt.add('size', default=1, vtype=int, doc="The point size, if None then no points are shown.")
    return opt

def applyOptions(vtkactor, opt):

    """
    if opt.isValid('orientation'):
        vtkactor.SetOrientation(opt.get('orientation'))

    x, y, z = opt.get('rotation')
    vtkactor.RotateX(x)
    vtkactor.RotateY(y)
    vtkactor.RotateZ(z)
    """

    vtkactor.GetProperty().SetEdgeVisibility(opt.get('visible'))
    vtkactor.GetProperty().SetEdgeColor(opt.get('color'))
    vtkactor.GetProperty().SetLineWidth(opt.get('width'))
    vtkactor.GetProperty().SetPointSize(opt.get('size'))
