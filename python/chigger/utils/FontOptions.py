#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from Options import Options



def validOptions(prefix=None): #pylint: disable=invalid-name
    """
    Returns options for vtk fonts.
    """
    key = lambda x: '{}_{}'.format(prefix, x) if prefix else x

    opt = Options()
    opt.add(key('color'), (1., 1., 1.), doc="The text color.", vtype=float, size=3)
    opt.add(key('shadow'), False, doc="Toggle text shadow.", vtype=bool)
    opt.add(key('halign'), 'left', doc="Set the font justification.", vtype=str,
            allow=('left', 'center', 'right'))
    opt.add(key('valign'), 'bottom', doc="The vertical text justification.",
            allow=('bottom', 'middle', 'top'))
    opt.add(key('opacity'), 1., doc="The text opacity.", vtype=float)
    opt.add(key('size'), 24, doc="The text font size.", vtype=int)
    return opt

def applyOptions(tprop, opt, prefix=None): #pylint: disable=invalid-name
    """
    Applies font options to vtkTextProperty object.

    Inputs:
        tprop: A vtk.vtkTextProperty object for applying options.
        options: The Options object containing the settings to apply.
    """
    key = lambda x: '{}_{}'.format(prefix, x) if prefix else x

    opt.setOption(key('color'), tprop.SetColor, prefix=prefix)
    opt.setOption(key('shadow'), tprop.SetShadow, prefix=prefix)


    """
    if options.isOptionValid('justification'):
        idx = options.raw('justification').allow.index(options.get('justification'))
        tprop.SetJustification(idx)

    if options.isOptionValid('vertical_justification'):
        idx = options.raw('vertical_justification').allow.index(
            options.get('vertical_justification'))
        tprop.SetVerticalJustification(idx)

    if options.isOptionValid('opacity'):
        tprop.SetOpacity(options.get('opacity'))

    if options.isOptionValid('size'):
        tprop.SetFontSize(options.get('size'))
    """
