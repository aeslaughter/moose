from parameters import InputParameters

def validParams():
    """Returns options for edge properties for vtkActor objects."""
    params = InputParameters()
    params.add('enable', default=False, doc="Enable/disable display of object edges.")
    params.add('color', default=(1., 1., 1.), size=3, doc="Set the edge color.")
    params.add('width', default=1, vtype=int, doc="The edge width, if None then no edges are shown.")
    return params

def setParams(obj, params):
    if params.isValid('enable'):
        obj.getVTKActor().GetProperty().SetEdgeVisibility(params.get('enable'))
    if params.isValid('color'):
        obj.getVTKActor().GetProperty().SetEdgeColor(params.get('color'))
    if params.isValid('width'):
        obj.getVTKActor().GetProperty().SetLineWidth(params.get('width'))
