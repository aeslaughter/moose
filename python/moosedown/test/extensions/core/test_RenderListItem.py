#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderListItemHTML(testing.MooseDocsTestCase):

    def testWrite(self):
        node = tree.tokens.UnorderedList(None)
        tree.tokens.ListItem(node)
        html = self.write(self.render(node).find('body')(-1))
        self.assertEqual(html, '<ul><li></li></ul>')

    def testError(self):
        with self.assertRaises(IOError) as e:
            tree.tokens.ListItem(None)
        self.assertIn("A 'ListItem' must have a 'OrderedList' or 'UnorderedList' parent.",
                      str(e.exception))


class TestRenderListItemMaterialize(TestRenderListItemHTML):
    RENDERER = MaterializeRenderer
    def testWrite(self):
        node = tree.tokens.UnorderedList(None)
        tree.tokens.ListItem(node)
        html = self.write(self.render(node).find('body')(0)(0))
        self.assertEqual(html, '<ul class="browser-default"><li></li></ul>')

class TestRenderListItemLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testWrite(self):
        ast = tree.tokens.UnorderedList(None)
        tree.tokens.ListItem(ast)
        node = self.render(ast).find('document')(-1)
        tex = self.write(node).strip('\n')
        self.assertString(tex, '\\begin{itemize}\n\\item\n\\end{itemize}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
