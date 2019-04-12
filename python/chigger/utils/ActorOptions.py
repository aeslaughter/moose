from Options import Options
#from EdgeOptions import EdgeOptions

def validOptions():
    """Returns options for edge properties for vtkActor objects."""
    opt = Options()

    opt.add('opacity', default=1., vtype=float, doc="The object opacity.")
    opt.add('color', vtype=float, size=3, doc="The color of the object.")
    #opt.add('edges', EdgeOptions.validOptions(), vtype=Options, doc="Edge options.")
    return opt

def applyOptions(vtkactor, opt):
    vtkactor.GetProperty().SetOpacity(opt.get('opacity'))
    vtkactor.GetProperty().SetColor(opt.get('color'))
    #EdgeOptions.applyOptions(vtkactor, opt['edges'])
