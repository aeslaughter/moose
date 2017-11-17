#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderCodeHTML(testing.MarkdownTestCase):
    """Code HTML"""

    def testTree(self):
        node = self.render('```\nint x;\n```').find('pre')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.Tag)
        self.assertIsInstance(node(0)(0), tree.html.String)

        self.assertEqual(node.name, 'pre')
        self.assertEqual(node(0).name, 'code')
        self.assertString(node(0)['class'], 'language-text')
        self.assertString(node(0)(0).content, '\nint x;\n')

    def testWrite(self):
        node = self.render('```\nint x;\n```').find('pre')
        html = self.write(node)
        self.assertString(html, '<pre><code class="language-text">\nint x;\n</code></pre>')

    def testTreeLanguage(self):
        node = self.render('```language=cpp\nint x;\n```').find('pre')
        self.assertString(node(0)['class'], 'language-cpp')

    def testWriteLanguage(self):
        node = self.render('```language=cpp\nint x;\n```').find('pre')
        html = self.write(node)
        self.assertString(html, '<pre><code class="language-cpp">\nint x;\n</code></pre>')


class TestRenderCodeMaterialize(TestRenderCodeHTML):
    """Code Materialize"""
    RENDERER = MaterializeRenderer


class TestRenderCodeLatex(testing.MarkdownTestCase):
    pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
