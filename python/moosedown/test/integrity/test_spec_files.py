#!/usr/bin/env python
import os
import sys
import unittest
import inspect
import pkgutil
import glob

import moosedown
from moosedown import extensions
from moosedown.common import testing
from moosedown.base import testing, TokenComponent, RenderComponent
from moosedown.base import MarkdownExtension, RenderExtension

import hit

class TestSpecFiles(unittest.TestCase):
    """
    Tests that all unittest classes are listed in a tests spec file.
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
                        if (child.type() != hit.NodeType.Blank) and
                           (child.find('type').param() == 'PythonUnitTest'):
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
            tests = testing.get_parent_objects(mod, unittest.TestCase)
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

if __name__ == '__main__':
    unittest.main(verbosity=2)
