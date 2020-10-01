#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import vtk
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import mooseutils
from .Options import Options



# TODO: UseAboveRangeColorOn ()

def validOptions():
    """Return options for color maps creation"""
    opt = Options()

    cmap = Options()
    cmap.add('name', vtype=str, doc="The colormap name.")
    cmap.add('reverse', default=False, vtype=bool,
            doc="Reverse the order of colormap.")
    cmap.add('resolution', default=256, vtype=int,
             doc="Number of colors to utilize")
    cmap.add('lim', default=(0, 1), vtype=(float, int), size=2,
             doc="Set the data range for the color map to display.")
    cmap.add('above', vtype=(int, float), size=4, doc="Above out-of-range color (R,G,B, alpha)")
    cmap.add('below', vtype=(int, float), size=4, doc="Below out-of-range color (R,G,B, alpha)")
    cmap.add('nan', vtype=(int, float), size=4, doc="NaN out-of-range color (R,G,B, alpha)")
    opt.add('cmap', default=cmap, vtype=Options, doc='Color map options')
    return opt

def applyOptions(opt):
    """
    Applies color map options and returns a vtk.vtkTable for use
    """
    lut = vtk.vtkLookupTable()

    if not opt.isValid('name'):
        hue = (0., 0.667) if opt.get('reverse') else (0.667, 0.)
        lut.SetHueRange(*hue)
    else:
        name = opt.get('name')
        n = opt.get('resolution')
        points = np.linspace(0, 1, n)
        cmap = getattr(cm, name)(points)
        rng = reversed(range(n)) if opt.get('reverse') else range(n)
        for i, r in enumerate(rng):
            lut.SetTableValue(i, *cmap[r])

    opt.assign('resolution', lut.SetNumberOfColors)
    opt.assign('above', lut.SetAboveRangeColor)
    opt.assign('below', lut.SetBelowRangeColor)
    opt.assign('nan', lut.SetNanColor)
    return lut
