#!/usr/bin/env python
import unittest
import mock
import tempfile
#import moosedown
#from moosedown import extensions
#from moosedown.base import testing, TokenComponent, RenderComponent
from moosedown.tree import page
from moosedown.base import testing# MarkdownExtension, RenderExtension

#import hit

class TestErrorHandling(testing.MooseDocsTestCase):

    def content(self):
        return u'This is some text that contains a command\n\n!unkown command\n, it should error ' \
               u'during tokenize.\n\n!this too\n\n'

    @mock.patch('logging.Logger.exception')
    def testFromText(self, mock):
        ast = self.ast(self.content())

        self.assertEqual(mock.call_count, 2)

        calls = mock.call_args_list
        args, kwargs = calls[0]
        self.assertEqual(len(args), 1)
        self.assertIn("An exception occurred on line 3 while tokenizing", args[0])
        self.assertIn("moosedown.extensions.core.Command", args[0])
        self.assertIn("The following command combination is unknown: 'unkown command'", args[0])

        args, kwargs = calls[1]
        self.assertEqual(len(args), 1)
        self.assertIn("An exception occurred on line 6 while tokenizing", args[0])
        self.assertIn("moosedown.extensions.core.Command", args[0])
        self.assertIn("The following command combination is unknown: 'this too'", args[0])

    @mock.patch('logging.Logger.exception')
    def testFromFile(self, mock):
        filename = tempfile.mkstemp('.md')[-1]
        with open(filename, 'w') as fid:
            fid.write(self.content())

        node = page.MarkdownNode(None, source=filename)
        node.read()
        ast = self._translator.ast(node)

        self.assertEqual(mock.call_count, 2)

        calls = mock.call_args_list
        args, kwargs = calls[0]
        self.assertEqual(len(args), 1)
        self.assertIn(filename + ':3', args[0])
        self.assertIn("moosedown.extensions.core.Command", args[0])
        self.assertIn("The following command combination is unknown: 'unkown command'", args[0])

        args, kwargs = calls[1]
        self.assertEqual(len(args), 1)
        self.assertIn(filename + ':6', args[0])
        self.assertIn("moosedown.extensions.core.Command", args[0])
        self.assertIn("The following command combination is unknown: 'this too'", args[0])

        if os.path.exists(filename):
            os.remove(filename)





if __name__ == '__main__':
    unittest.main(verbosity=2)
