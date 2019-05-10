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
    opt.setOption('color', vtkactor.GetProperty().SetColor)
    opt.setOption('opacity', vtkactor.GetProperty().SetOpacity)
    opt.setOption('linewidth', vtkactor.GetProperty().SetLineWidth)
