#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

from .Options import Options
def validOptions():
    """Returns options for vtkTextProperty."""
    opt = Options()
    opt.add('color', vtype=float, size=3, doc="The text color.")
    opt.add('shadow', default=False, vtype=bool, doc="Toggle text shadow.")
    opt.add('halign', default='left', vtype=str, allow=('left', 'center', 'right'),
            doc="Set the font justification.")
    opt.add('valign', default='bottom', allow=('bottom', 'middle', 'top'),
            doc="The vertical text justification.")
    opt.add('opacity', default=1., vtype=float,
            verify=(lambda v: v>=0 and v<=1, "The supplied value must in range [0,1]"),
            doc="The text opacity.")
    opt.add('size', default=24, vtype=int, doc="The text font size.")
    opt.add('italic', default=False, vtype=bool, doc="Toggle the text italics.")
    opt.add('orientation', vtype=int, doc="Text orientation in degrees.")
    opt.add('frame', vtype=bool, default=False, doc="Add a frame around the text.")
    opt.add('frame_color', vtype=float, size=3, doc="The color of the frame around text.")
    opt.add('frame_width', vtype=int, doc="The width of the frame around text.")
    opt.add('background_color', vtype=float, size=3, doc="The color of the text background.")
    opt.add('background_opacity', default=1, vtype=float,
            verify=(lambda v: v>=0 and v<=1, "The supplied value must in range [0,1]"),
            doc="The opacity of the text background.")
    opt.add('rotate', default=0., vtype=float,
            verify=(lambda v: v>=0 and v<=360, "The supplied value must in range [0,360]"),
            doc="The text rotation in degrees.")
    return opt

def applyOptions(tprop, opt, prefix=None): #pylint: disable=invalid-name
    """
    Applies font options to vtkTextProperty object.

    Inputs:
        tprop: A vtk.vtkTextProperty object for applying options.
        options: The Options object containing the settings to apply.
    """
    opt.assign('color', tprop.SetColor)
    opt.assign('shadow', tprop.SetShadow)
    opt.assign('opacity', tprop.SetOpacity)
    opt.assign('size', tprop.SetFontSize)
    opt.assign('italic', tprop.SetItalic)
    opt.assign('orientation', tprop.SetOrientation)
    opt.assign('frame', tprop.SetFrame)
    opt.assign('frame_color', tprop.SetFrameColor)
    opt.assign('frame_width', tprop.SetFrameWidth)
    opt.assign('background_color', tprop.SetBackgroundColor)
    opt.assign('background_opacity', tprop.SetBackgroundOpacity)
    opt.assign('rotate', tprop.SetOrientation)
    #tprop.UseTightBoundingBoxOn()

    halign = opt.get('halign')
    if halign == 'left':
        tprop.SetJustificationToLeft()
    if halign == 'center':
        tprop.SetJustificationToCentered()
    if halign == 'right':
        tprop.SetJustificationToRight()

    valign = opt.get('valign')
    if halign == 'left':
        tprop.SetVerticalJustificationToBottom()
    if halign == 'center':
        tprop.SetVerticalJustificationToCentered()
    if halign == 'right':
        tprop.SetVerticalJustificationToTop()
