from Options import Options
#from EdgeOptions import EdgeOptions

def validOptions():
    """Returns options for edge properties for vtkActor objects."""
    opt = Options()
    opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
    opt.add('color', vtype=float, size=3, doc="The color of the object.")
    opt.add('linewidth', 1, vtype=float, doc="The line width for the object.")
    return opt

def applyOptions(vtkactor, opt):
    opt.assign('color', vtkactor.GetProperty().SetColor)
    opt.assign('opacity', vtkactor.GetProperty().SetOpacity)
    opt.assign('linewidth', vtkactor.GetProperty().SetLineWidth)
