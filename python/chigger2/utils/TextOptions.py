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
def validOptions(): #pylint: disable=invalid-name
    """
    Returns options for vtk fonts.
    """
    #key = lambda x: '{}_{}'.format(prefix, x) if prefix else x

    opt = Options()
    opt.add('color', None, doc="The text color.", vtype=float, size=3)
    opt.add('shadow', False, doc="Toggle text shadow.", vtype=bool)
    opt.add('halign', 'left', doc="Set the font justification.", vtype=str,
            allow=('left', 'center', 'right'))
    opt.add('valign', 'bottom', doc="The vertical text justification.",
            allow=('bottom', 'middle', 'top'))
    opt.add('opacity', 1., doc="The text opacity.", vtype=float)
    opt.add('size', 24, doc="The text font size.", vtype=int)
    opt.add('italic', False, doc="Toggle the text italics.")
    opt.add('orientation', vtype=int, doc="Text orientation in degrees.")


    #opt.add(key('fontcolor'), None, doc="The text color.", vtype=float, size=3)
    #opt.add(key('fontshadow'), False, doc="Toggle text shadow.", vtype=bool)
    #opt.add(key('fonthalign'), 'left', doc="Set the font justification.", vtype=str,
    #        allow=('left', 'center', 'right'))
    #opt.add(key('fontvalign'), 'bottom', doc="The vertical text justification.",
    #        allow=('bottom', 'middle', 'top'))
    #opt.add(key('fontopacity'), 1., doc="The text opacity.", vtype=float)
    #opt.add(key('fontsize'), 24, doc="The text font size.", vtype=int)
    #opt.add(key('fontitalic'), False, doc="Toggle the text italics.")
    #opt.add(key('orientation'), vtype=int, doc="Text orientation in degrees.")
    #if unset:
    #    for k in opt.keys():
    #        opt.set(k, None)

    return opt

def applyOptions(tprop, opt, prefix=None): #pylint: disable=invalid-name
    """
    Applies font options to vtkTextProperty object.

    Inputs:
        tprop: A vtk.vtkTextProperty object for applying options.
        options: The Options object containing the settings to apply.
    """
    key = lambda x: '{}_{}'.format(prefix, x) if prefix else x

    opt.assign(key('color'), tprop.SetColor)
    opt.assign(key('shadow'), tprop.SetShadow)
    opt.assign(key('opacity'), tprop.SetOpacity)
    opt.assign(key('size'), tprop.SetFontSize)
    opt.assign(key('italic'), tprop.SetItalic)
    opt.assign(key('orientation'), tprop.SetOrientation)

    tprop.UseTightBoundingBoxOn()

    halign = key('halign')
    if opt.isOptionValid(halign):
        idx = opt.raw(halign).allow.index(opt.get(halign))
        tprop.SetJustification(idx)

    valign = key('valign')
    if opt.isOptionValid(valign):
        idx = opt.raw(valign).allow.index(
            opt.get(valign))
        tprop.SetVerticalJustification(idx)
