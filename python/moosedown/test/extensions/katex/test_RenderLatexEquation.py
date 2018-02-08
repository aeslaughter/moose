#!/usr/bin/env python
import unittest
import moosedown
from moosedown.base import testing, renderers
from moosedown.tree import html

TEXT = u'$ax+b$\n\n\\begin{equation}\nE=mc^2\n\\end{equation}'

class TestRenderLatexEquationHTML(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    def node(self):
        return self.render(TEXT)

    def testTree(self):
        node = self.node()

        # Inline
        self.assertIsInstance(node(0), html.Tag)
        self.assertEqual(node(0).name, 'p')
        self.assertIsInstance(node(0)(0), html.Tag)
        self.assertEqual(node(0)(0).name, 'span')
        self.assertIsInstance(node(0)(0)(0), html.Tag)
        self.assertEqual(node(0)(0)(0).name, 'script')
        self.assertIsInstance(node(0)(0)(0)(0), html.String)
        self.assertIn('moose-equation-', node(0)(0)(0)(0).content)
        self.assertIn('katex.render("ax+b', node(0)(0)(0)(0).content)
        self.assertIn('displayMode:false', node(0)(0)(0)(0).content)

        # Block
        self.assertIsInstance(node(1), html.Tag)
        self.assertEqual(node(1).name, 'div')
        self.assertIsInstance(node(1)(0), html.Tag)
        self.assertEqual(node(1)(0).name, 'div')
        self.assertIsInstance(node(1)(1), html.Tag)
        self.assertEqual(node(1)(1).name, 'div')
        self.assertIsInstance(node(1)(1)(0), html.String)
        self.assertIn('(1)', node(1)(1)(0).content)

        self.assertIsInstance(node(1)(2), html.Tag)
        self.assertEqual(node(1)(2).name, 'script')
        self.assertIsInstance(node(1)(2)(0), html.String)
        self.assertIn('moose-equation-', node(1)(2)(0).content)
        self.assertIn('katex.render("E=mc^2', node(1)(2)(0).content)
        self.assertIn('displayMode:true', node(1)(2)(0).content)

    def testWrite(self):
        pass
        #node = self.node()
        #html = node.write()
        #self.assertString(html, '<p>foo bar</p>')

class TestRenderLatexEquationMaterialize(TestRenderLatexEquationHTML):
    RENDERER = renderers.MaterializeRenderer
    def node(self):
        return self.render(TEXT).find('body')(0)(0)(0)

class TestRenderLatexEquationLatex(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.katex]
    RENDERER = renderers.LatexRenderer
    def testTree(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
