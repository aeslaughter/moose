#!/usr/bin/env python
import os
import sys
import unittest
import inspect
import pkgutil
import glob

import moosedown
from moosedown import extensions
from moosedown.base import testing, TokenComponent, RenderComponent
from moosedown.base import MarkdownExtension, RenderExtension

import hit

class TestIntegrity(unittest.TestCase):
    """
    A top-level unittest that checks various components of the existing tests, including
    that all extensions have there components tested and that all unittest.TestCase objects
    have an entry in a tests spec file.
    """
    def check(self, location):
        """
        Check the test directory.
        """

        # List of errors
        messages = []

        # Load the test spec and create a list of PythonUnitTest files
        tested = set()

        spec = os.path.join(location, 'tests')
        if os.path.exists(spec):
            with open(spec, 'r') as fid:
                data = fid.read()
                node = hit.parse(spec, data)
                for block in node.children():
                    for child in block.children():
                        if child.type() != hit.NodeType.Blank and child.find('type').param() == 'PythonUnitTest':
                            tested.add(child.find('input').param())

        # Loop through python files in this directory
        for filename in glob.glob(os.path.join(location, '*.py')):

            # Local filename
            base = os.path.basename(filename)

            # Load the module (tried this with os.chdir, but that didn't work)
            sys.path.append(location)
            mod = __import__(base[:-3])
            sys.path.remove(location)

            # Get a lit of unittest.TestCase objects, if they exist this file should be in spec
            tests = get_parent_objects(mod, unittest.TestCase)
            if tests and (base not in tested):
                msg = "The test script '{}' is not included in the tests spec '{}'."
                messages.append(msg.format(base, spec))

        return messages

    def testSpec(self):
        """
        Test that all unittest.TestCases have an entry in a tests spec file.
        """

        messages = []
        location = os.path.join(os.path.dirname(moosedown.__file__), 'tests')
        for root, dirs, _ in os.walk(location):
            for d in dirs:
                messages += self.check(os.path.join(root, d))

        self.assertFalse(messages, '\n'.join(messages))

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
    BASE = [extensions.core.List,
            extensions.core.MarkdownComponent,
            extensions.core.CoreRenderComponentBase]


    @classmethod
    def setUpClass(cls):
        """
        Create a list of extensions, if it is not defined.
        """

        # TODO: Fix detetection of modules
        """
        if cls.EXTENSIONS is None:
            cls.EXTENSIONS = []
            loc = os.path.dirname(moosedown.extensions.__file__)
            sys.path.append(loc)
            for item in dir(moosedown.extensions):
                if item.startswith('__'):
                    continue
                cls.EXTENSIONS.append(__import__(item))
            sys.path.remove(loc)
        print cls.EXTENSIONS
        """
    def testReaderComponents(self):
        """
        Test TokenComponent testing
        """
        messages = []
        for ext in self.EXTENSIONS:
            messages += check_component(ext, TokenComponent, self.READER_REQUIRED, self.BASE)
        self.assertFalse(messages, '\n'.join(messages))

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
        for ext in self.EXTENSIONS:
            self.assertTrue(hasattr(ext, 'make_extension'), "Missing 'make_extension' function.")

            reader_ext, render_ext = ext.make_extension()
            self.assertIsInstance(reader_ext, MarkdownExtension)
            self.assertIsInstance(render_ext, RenderExtension)


def get_parent_objects(module, cls):
    """
    Tool for locating all objects that derive from a certain base class.
    """
    func = lambda obj: inspect.isclass(obj) and issubclass(obj, cls)
    return inspect.getmembers(module, predicate=func)


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
