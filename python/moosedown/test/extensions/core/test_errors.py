#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestErrors(testing.MooseDocsTestCase):

    @mock.patch('logging.Logger.error')
    def testUnknownSettings(self, mock):
        html = self.render(u'# Heading with Spaces foo=bar')
        h = html(0)
        mock.assert_called_once()
        self.assertIsInstance(h, tree.html.Tag)
        self.assertEqual(h.name, 'div')
        self.assertEqual(h(0).content, '# Heading with Spaces foo=bar')
        self.assertString(h.write(), '<div class="moose-exception"># Heading with Spaces foo=bar</div>')

if __name__ == '__main__':
    unittest.main(verbosity=2)
