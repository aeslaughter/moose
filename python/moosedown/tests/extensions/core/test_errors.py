#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestErrors(testing.MarkdownTestCase):

    def testUnknownSettings(self):
        #with self.assertRaises(KeyError) as e:
        html = self.render(u'# Heading with Spaces foo=bar')
        h = html(0)

        self.assertIsInstance(h, tree.html.Tag)
        self.assertEqual(h.name, 'div')
        self.assertEqual(h(0).content, '# Heading with Spaces foo=bar')
        """
        # Check error message
        mock.assert_called_once()
        args, kwargs = mock.call_args
        self.assertIn('The following key, value settings are unknown', args[0])
        self.assertIn("foo='bar'", args[0])
        """
        self.assertString(h.write(), '<div class="moose-exception"># Heading with Spaces foo=bar</div>')

if __name__ == '__main__':
    unittest.main(verbosity=2)
