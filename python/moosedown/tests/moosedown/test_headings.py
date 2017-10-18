#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import MooseMarkdown
from moosedown import tree

class TestHeadings(unittest.TestCase):

    def ast(self, md):
        markdown = MooseMarkdown.MooseMarkdown(materialize=False)
        return markdown.ast(md)

    def html(self, md):
        markdown = MooseMarkdown.MooseMarkdown(materialize=False)
        return markdown.convert(md)

    def testBasic(self):
        ast = self.ast('# Heading with Spaces')
        h = ast(0)
        self.assertIsInstance(h, tree.tokens.Heading)
        self.assertEqual(h.level, 1)
        self.assertIsInstance(h(0), tree.tokens.Word)
        self.assertIsInstance(h(1), tree.tokens.Space)
        self.assertIsInstance(h(2), tree.tokens.Word)
        self.assertIsInstance(h(3), tree.tokens.Space)
        self.assertIsInstance(h(4), tree.tokens.Word)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(4).content, 'Spaces')

    def testLevels(self):
        for i in range(1,7):
            ast = self.ast('{} Heading'.format('#'*i))
            self.assertEqual(ast(0).level, i)

    def testHTML(self):
        html = self.html('# Heading with Spaces')
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

    def testHTMLSettings(self):
        html = self.html('# Heading with Spaces style=font-size:42pt;')
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
        self.assertEqual(h['style'], 'font-size:42pt;')

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
