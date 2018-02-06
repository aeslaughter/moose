#!/usr/bin/env python
import os
import sys
import unittest
import inspect
import importlib

import moosedown
from moosedown.base import testing, components

import hit

class TestExtensions(testing.MooseDocsTestCase):
    """
    Tests that Extension objects have the

    """
    EXTENSIONS = [moosedown.extensions.core]
    READER_REQUIRED = set(['Test{}Tokenize'])
    RENDER_REQUIRED = set(['Test{}HTML', 'Test{}Materialize', 'Test{}Latex'])

    def testReaderComponents(self):
        """
        Test TokenComponent testing
        """
        messages = []
        for comp in self._reader.components:
            messages += self.checkComponent(comp, self.READER_REQUIRED)
        self.assertFalse(messages, '\n' + '\n'.join(messages))

    def testRenderComponents(self):
        """
        Test RenderComponent testing
        """
        messages = []
        for comp in self._renderer.components:
            messages += self.checkComponent(comp, self.RENDER_REQUIRED)
        self.assertFalse(messages, '\n' + '\n'.join(messages))

    @staticmethod
    def checkComponent(component, required):
        """
        Tool for inspecting the existence of the necessary test objects.

        Inputs:
            ext: The component instance to inspect
            required: List of required test objects format strings (e.g., ['Test{}Foo', 'Test{}Bar'])
        """
        path = os.path.abspath(os.path.join(os.getcwd(), '..',
                               *str(component.__module__).split('.')[1:]))
        name = component.__class__.__name__
        testname = 'test_{}.py'.format(name)
        filename = os.path.join(path, testname)

        messages = []
        if not os.path.exists(filename):
            msg = "'{}' needs to be created in {}.".format(testname, path)
            messages.append(msg)
        else:
            sys.path.append(path)
            module = importlib.import_module(testname[:-3])
            tests = set([obj[0] for obj in testing.get_parent_objects(module, unittest.TestCase)])
            req = set([r.format(name) for r in required])
            for missing in req.difference(tests):
                msg = "'{}' must be added to '{}' in {}.".format(missing, testname, path)
                messages.append(msg)
            sys.path.remove(path)
        return messages

if __name__ == '__main__':
    unittest.main(verbosity=2)
