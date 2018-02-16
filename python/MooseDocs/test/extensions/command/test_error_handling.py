#!/usr/bin/env python
import os
import unittest
import mock
import tempfile

import moosedown
from moosedown.tree import page
from moosedown.base import testing

class TestErrorHandling(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.command]

    def content(self):
        return u'This is some text that contains a command\n\n!unkown command\n, it should error ' \
               u'during tokenize.\n\n!this too\n\n'

    @mock.patch('logging.Logger.error')
    def testFromText(self, mock):
        ast = self.ast(self.content())

        self.assertEqual(mock.call_count, 2)

        calls = mock.call_args_list
        args, kwargs = calls[0]
        msg = '\n'.join(args)
        self.assertIn("An error occurred on line 1 while tokenizing", msg)
        self.assertIn("The following command combination is unknown: 'unkown command'", msg)

        args, kwargs = calls[1]
        msg = '\n'.join(args)
        self.assertIn("An error occurred on line 4 while tokenizing", msg)
        self.assertIn("The following command combination is unknown: 'this too'", msg)

    @mock.patch('logging.Logger.error')
    def testFromFile(self, mock):
        filename = tempfile.mkstemp('.md')[-1]
        with open(filename, 'w') as fid:
            fid.write(self.content())

        node = page.MarkdownNode(None, source=filename)
        node.read()
        ast = self.ast(node)

        self.assertEqual(mock.call_count, 2)

        calls = mock.call_args_list
        args, kwargs = calls[0]
        msg = '\n'.join(args)
        self.assertIn("The following command combination is unknown: 'unkown command'", msg)

        args, kwargs = calls[1]
        msg = '\n'.join(args)
        self.assertIn("The following command combination is unknown: 'this too'", msg)

        if os.path.exists(filename):
            os.remove(filename)





if __name__ == '__main__':
    unittest.main(verbosity=2)
