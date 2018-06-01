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

def validOptions():
    """
    Returns options for vtk fonts.
    """
    opt = Options()
    opt.add('text_color', (1., 1., 1.), "The text color.", vtype=float, size=3)
    opt.add('text_shadow', False, "Toggle text shadow.", vtype=bool)
    opt.add('justification', 'left', "Set the font justification.", vtype=str,
            allow=('left', 'center', 'right'))
    opt.add('vertical_justification', 'bottom', "The vertical text justification.",
            allow=('bottom', 'middle', 'top'))
    opt.add('text_opacity', 1., "The text opacity.", vtype=float)
    opt.add('font_size', 24, "The text font size.", vtype=int)
    return opt


def applyOptions(tprop, options):
    """
    Applies font options to vtkTextProperty object.

    Inputs:
        tprop: A vtk.vtkTextProperty object for applying options.
        options: The Options object containing the settings to apply.
    """

    if options.isOptionValid('text_color'):
        tprop.SetColor(options.applyOption('text_color'))

    if options.isOptionValid('text_shadow'):
        tprop.SetShadow(options.applyOption('text_shadow'))

    if options.isOptionValid('justification'):
        idx = options.raw('justification').allow.index(options.applyOption('justification'))
        tprop.SetJustification(idx)

    if options.isOptionValid('vertical_justification'):
        idx = options.raw('vertical_justification').allow.index(options.applyOption('vertical_justification'))
        tprop.SetVerticalJustification(idx)

    if options.isOptionValid('text_opacity'):
        tprop.SetOpacity(options.applyOption('text_opacity'))

    if options.isOptionValid('font_size'):
        tprop.SetFontSize(options.applyOption('font_size'))
