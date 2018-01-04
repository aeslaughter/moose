#!/usr/bin/env python
import unittest

from moosedown.commands.build import DEFAULT_EXTENSIONS, load_extensions
import hit


class TestLoadExtensions(unittest.TestCase):
    """
    Test load_extensions method
    """

    def testEmpty(self):
        """
        Test t
        """
        err = []
        ext = load_extensions(None, errors=err)
        names = set([e.__module__ for e in ext])
        self.assertEqual(names, DEFAULT_EXTENSIONS)
        self.assertEqual(err, [])

    def testDisableDefaults(self):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))

        err = []
        ext = load_extensions(ext, errors=[])

        self.assertEqual(ext, [])
        self.assertEqual(err, [])

    def testMissingTypeError(self):
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        ext.addChild(hit.NewSection('foo'))

        err = []
        ext = load_extensions(ext, errors=err)
        
        self.assertEqual(ext, [])
        self.assertEqual(len(err), 1)
        self.assertEqual("The section 'foo' must contain a 'type' parameter.", err[0][0])



if __name__ == '__main__':
    unittest.main(verbosity=2)
