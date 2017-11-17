#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestErrors(testing.MarkdownTestCase):

    @mock.patch('logging.Logger.error')
    def testUnknownSettings(self, mock):
        html = self.html('# Heading with Spaces foo=bar')
        h = html(0)
        self.assertIsInstance(h, tree.html.Tag)
        self.assertEqual(h.name, 'h1')
        for child in h.children:
            self.assertIsInstance(child, tree.html.String)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(1).content, ' ')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(3).content, ' ')
        self.assertEqual(h(4).content, 'Spaces')

        # Check error message
        mock.assert_called_once()
        args, kwargs = mock.call_args
        self.assertIn('The following key, value settings are unknown', args[0])
        self.assertIn("foo='bar'", args[0])

        self.assertString(h.write(), "<h1>Heading with Spaces</h1>")

if __name__ == '__main__':
    unittest.main(verbosity=2)
