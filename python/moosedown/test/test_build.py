#!/usr/bin/env python
import unittest
import mock

from moosedown.commands.build import DEFAULT_EXTENSIONS, load_extensions, load_translator
import hit


class TestLoadExtensions(unittest.TestCase):
    """
    Test load_extensions method
    """

    def testEmpty(self):
        """
        Check that excluding [Extensions] section creates the defaults.
        """
        ext = load_extensions(None, 'foo')
        names = set([e.__module__ for e in ext])
        self.assertEqual(names, DEFAULT_EXTENSIONS)

    def testDisableDefaults(self):
        """
        Check that defaults can be disabled.
        """
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))

        ext = load_extensions(ext, '')
        self.assertEqual(ext, [])

    @mock.patch('logging.Logger.error')
    def testMissingTypeError(self, mock):
        """
        Test error when Extensions section are missing type.
        """
        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        ext.addChild(hit.NewSection('foo'))

        ext = load_extensions(ext, 'foo')
        self.assertEqual(ext, [])

        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn("The section '%s' must contain a 'type' parameter.", args[0])

    @mock.patch('logging.Logger.error')
    def testModuleImportError(self, mock):
        """
        Test error that a bad extension name errors.
        """

        ext = hit.NewSection('Extensions')
        ext.addChild(hit.NewField('disable_defaults', hit.FieldKind.Bool, 'True'))
        foo = hit.NewSection('foo')
        foo.addChild(hit.NewField('type', hit.FieldKind.String, 'Bad'))
        ext.addChild(foo)

        ext = load_extensions(ext, 'foo')

        self.assertEqual(ext, [])
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertEqual("Failed to import the '%s' module.", args[0])

class TestLoadTranslator(unittest.TestCase):
    def testEmpty(self):
        pass
        """
        err = []
        tran = load_translator(None, err)
        self.assertIsInstance(tran, moosedown.base.Translator)
        self.assertEqual(err, [])
        """


if __name__ == '__main__':
    unittest.main(verbosity=2)
