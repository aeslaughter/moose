#!/usr/bin/env python
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html

"""
This example tests the various modes of interaction available in chigger: None, native VTK, or
custom interaction (default).
"""
import sys
import os
import io
import unittest
from unittest.mock import patch
import vtk
from mooseutils.ImageDiffer import ImageDiffer
import chigger2 as chigger

class ChiggerTestCase(unittest.TestCase):

    def assertImage(self, basename, **kwargs):
        filename = '{}_{}'.format(self.__class__.__name__, basename)
        goldname = os.path.join(os.path.dirname(filename), 'gold', os.path.basename(filename))
        self._window.write(filename)

        """
        image = vtk.vtkPNGReader()
        image.SetFileName(filename)
        image.Update()

        gold = vtk.vtkPNGReader()
        gold.SetFileName(filename)
        gold.Update()

        diff = vtk.vtkImageDifference()
        diff.SetInputConnection(image.GetOutputPort())
        diff.SetImageConnection(gold.GetOutputPort())
        diff.SetThreshold(0)
        diff.Update()
        self.assertFalse(diff.GetError())
        """
        kwargs.setdefault('allowed', 0.99)
        diff = ImageDiffer(filename, goldname, **kwargs)
        print(diff.message())
        self.assertFalse(diff.fail())

class TestInteraction(ChiggerTestCase):
    def setUp(self):

        self._window = chigger.Window(size=(400, 400))
        self._tester = chigger.observers.TestObserver(self._window)

        left = chigger.Viewport(self._window, viewport=(0, 0, 0.5, 1))
        right = chigger.Viewport(self._window, viewport=(0.5, 0, 1, 1))

        rect0 = chigger.geometric.Rectangle(left, bounds=(0.25, 0.5, 0.25, 0.75), color=(0.5, 0.1, 0.2))
        cube0 = chigger.geometric.Cube(left, bounds=(0.5, 0.8, 0, 0.5, 0.8, 1), color=(0.1, 0.2, 0.8))

        rect1 = chigger.geometric.Rectangle(right, bounds=(0.25, 0.5, 0.25, 0.75), color=(0.2,0.1, 0.5))
        cube1 = chigger.geometric.Cube(right, bounds=(0.5, 0.8, 0, 0.5, 0.8, 1), color=(0.8, 0.2, 0.1))

    def tearDown(self):
        self._tester.terminate()

    @patch('sys.stdout', new_callable=io.StringIO)
    def testGeneralHelp(self, stdout):
        self._tester.keyPress('h')
        self.assertIn('General Keybindings:', stdout.getvalue())

        self.assertIn(' v:', stdout.getvalue())
        self.assertIn('Select the next Viewport', stdout.getvalue())
        self.assertIn('shift-v:', stdout.getvalue())
        self.assertIn('Select the previous Viewport', stdout.getvalue())

        self.assertIn(' s:', stdout.getvalue())
        self.assertIn('Select the next Source', stdout.getvalue())
        self.assertIn('shift-s:', stdout.getvalue())
        self.assertIn('Select the previous Source', stdout.getvalue())

        self.assertIn('r:', stdout.getvalue())
        self.assertIn('h:', stdout.getvalue())
        self._tester.terminate()

    @patch('sys.stdout', new_callable=io.StringIO)
    def testViewportHelp(self, stdout):
        self._tester.keyPress('v')
        self._tester.keyPress('h')
        self.assertIn('Current Viewport Keybindings', stdout.getvalue())

    @patch('sys.stdout', new_callable=io.StringIO)
    def testSourceHelp(self, stdout):
        self._tester.keyPress('s')
        self._tester.keyPress('h')
        self.assertIn('Current Source Keybindings', stdout.getvalue())

    def testSelectViewport(self):
        self.assertImage('initial.png')

        self._tester.keyPress('v')
        self.assertImage('viewport1.png')

        self._tester.keyPress('v')
        self.assertImage('viewport2.png')

        self._tester.keyPress('v')
        self.assertImage('viewport3.png')

        self._tester.keyPress('v')
        self.assertImage('initial.png')

        self._tester.keyPress('v', shift=True)
        self.assertImage('viewport3.png')

        self._tester.keyPress('v', shift=True)
        self.assertImage('viewport2.png')

        self._tester.keyPress('v', shift=True)
        self.assertImage('viewport1.png')

        self._tester.keyPress('v', shift=True)
        self.assertImage('initial.png')

    def testSelectSource(self):
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self.assertImage('source1.png')

        self._tester.keyPress('s')
        self.assertImage('source2.png')

        self._tester.keyPress('s')
        self.assertImage('source3.png')

        self._tester.keyPress('s')
        self.assertImage('source4.png')

        self._tester.keyPress('s')
        self.assertImage('initial.png')

        self._tester.keyPress('s', shift=True)
        self.assertImage('source4.png')

        self._tester.keyPress('s', shift=True)
        self.assertImage('source3.png')

        self._tester.keyPress('s', shift=True)
        self.assertImage('source2.png')

        self._tester.keyPress('s', shift=True)
        self.assertImage('source1.png')

        self._tester.keyPress('s', shift=True)
        self.assertImage('initial.png')

    def testReset(self):
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self.assertImage('source1.png')

        self._tester.keyPress('r')
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self.assertImage('source1.png')

        self._tester.keyPress('r', shift=True)
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self.assertImage('source2.png')

    def test2DInteractorZoom(self):
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self._tester.mouseMove(0.5, 0.5)
        self._tester.mouseWheelForward(5)
        self.assertImage('interact_forward_2d.png')

        self._tester.mouseWheelBackward(5)
        self._tester.keyPress('r')
        self.assertImage('initial.png')

        self._tester.keyPress('s')
        self._tester.mouseWheelBackward(5)
        self.assertImage('interact_backward_2d.png')

        self._tester.mouseWheelForward(5)
        self._tester.keyPress('r')
        self.assertImage('initial.png')

    def test2DInteractorTranslate(self):
        self.assertImage('initial.png')
        self._tester.keyPress('s')
        self._tester.mouseMove(0.5, 0.5)
        user = self._window.getVTKInteractorStyle()
        user._left_button_down = True
        user._move_origin = self._window.getVTKInteractor().GetEventPosition()
        self._tester.mouseMove(0.7, 0.5)
        user.onMouseMove(self._window.getVTKInteractorStyle(), None)
        self.assertImage('translate_2d.png')

        user._move_origin = self._window.getVTKInteractor().GetEventPosition()
        self._tester.mouseMove(0.5, 0.5)
        user.onMouseMove(self._window.getVTKInteractorStyle(), None)
        self._tester.keyPress('r')
        self.assertImage('initial.png')

    def testMouseSelect(self):
        self.assertImage('initial.png')
        self._tester.mouseMove(0.15, 0.5)
        self._tester.mousePressLeft()
        self.assertImage('source1.png')

        self._tester.mouseMove(0.65, 0.5)
        self._tester.mousePressLeft()
        self._tester.mousePressLeft()
        self.assertImage('source3.png')

        self._tester.mouseMove(0.5, 0.5)
        self._tester.mousePressLeft()
        self.assertImage('initial.png')
