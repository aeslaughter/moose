#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderListItemHTML(testing.MooseDocsTestCase):
    def node(self):
        node = tree.tokens.UnorderedList(None)
        tree.tokens.ListItem(node)
        return self._renderer.render(node).find('body')

    def testWrite(self):
        html = self.node()(0)
        self.assertEqual(html.write(), '<ul><li></li></ul>')

    def testError(self):
        with self.assertRaises(IOError) as e:
            tree.tokens.ListItem(None)
        self.assertIn("A 'ListItem' must have a 'OrderedList' or 'UnorderedList' parent.",
                      str(e.exception))

class TestRenderListItemMaterialize(TestRenderListItemHTML):
    RENDERER = MaterializeRenderer
    def testWrite(self):
        html = self.node()(0)(0)(0)(0)
        self.assertEqual(html.write(), '<ul class="browser-default"><li></li></ul>')

class TestRenderListItemLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testWrite(self):
        node = tree.tokens.UnorderedList(None)
        tree.tokens.ListItem(node)
        tex = self._renderer.render(node).find('document')(0)
        self.assertString(tex.write(), '\n\\begin{itemize}\n\n\\item\n\\end{itemize}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
