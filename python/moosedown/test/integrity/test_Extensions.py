#!/usr/bin/env python
import os
import sys
import unittest
import inspect
import pkgutil
import glob

import moosedown
from moosedown.base import testing, components

import hit

class TestExtensions(unittest.TestCase):
    """
    Tests that extension classes have the required parts and tests. This includes making
    sure the 'make_extensions' method is working as well as that there is a test for every
    TokenComponent and RenderComponent is defined.
    """
    EXTENSIONS = [moosedown.extensions.core]
    READER_REQUIRED = ['Test{}Tokenize']
    RENDER_REQUIRED = ['Test{}HTML', 'Test{}Materialize', 'Test{}Latex']

    """ Objects listed here are ignored because they are base class objects that are not
        designed for use."""
    BASE = []#extensions.core.List,
             #extensions.base.TokenComponent,
             #extensions.core.CoreRenderComponentBase]

    @unittest.skip("")
    def testReaderComponents(self):
        """
        Test TokenComponent testing
        """
        messages = []
        for ext in self.EXTENSIONS:
            messages += check_component(ext, TokenComponent, self.READER_REQUIRED, self.BASE)
        self.assertFalse(messages, '\n'.join(messages))

    @unittest.skip("")
    def testRenderComponents(self):
        """
        Test RenderComponent testing
        """
        messages = []
        for ext in self.EXTENSIONS:
            messages += check_component(ext, RenderComponent, self.RENDER_REQUIRED, self.BASE)
        self.assertFalse(messages, '\n'.join(messages))

    def testMakeExtension(self):
        """
        Test the 'make_extension' function
        """
        pass
        #for ext in self.EXTENSIONS:
        #    self.assertTrue(hasattr(ext, 'make_extension'), "Missing 'make_extension' function.")

        #    reader_ext, render_ext = ext.make_extension()
        #    self.assertIsInstance(reader_ext, MarkdownExtension)
        #    self.assertIsInstance(render_ext, RenderExtension)

def check_component(ext, cls, required, skip):
    """
    Tool for inspecting the existence of the necessary test objects.

    Inputs:
        ext: The module to inspect (e.g., core, devel)
        cls: The base class to search for (e.g., base.TokenComponent)
        required: List of required test objects format strings (e.g., ['Test{}Foo', 'Test{}Bar'])
    """

    local = os.path.join(os.getcwd(), *ext.__name__.split('.')[1:])
    sys.path.append(local)

    messages = []
    for name, cls in get_parent_objects(ext, cls):
        if cls in skip:
            continue
        filename = 'test_{}.py'.format(name)
        full_name = os.path.join(local, filename)
        if not os.path.exists(full_name):
            msg = "The test file for {} does't exists, create it as '{}'".format(name, full_name)
            messages.append(msg)
        else:
            spec = __import__(filename[:-3])
            tests = [obj[0] for obj in get_parent_objects(spec, unittest.TestCase)]
            for test_obj_format in required:
                test_obj_name = test_obj_format.format(name)
                if test_obj_name not in tests:
                    msg = "The test file '{}' doesn't contain the required '{}' unittest.TestCase object.".format(full_name, test_obj_name)
                    messages.append(msg)

    sys.path.remove(local)
    return messages




if __name__ == '__main__':
    unittest.main(verbosity=2)
