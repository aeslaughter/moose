#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderUnorderedListHTML(testing.MooseDocsTestCase):
    def node(self, text):
        return self.render(text)(0)

    def testTree(self):
        node = self.node(u'- foo\n- bar')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.Tag)
        self.assertIsInstance(node(1), tree.html.Tag)

        self.assertIsInstance(node(0)(0), tree.html.Tag)
        self.assertIsInstance(node(1)(0), tree.html.Tag)

        self.assertIsInstance(node(0)(0)(0), tree.html.String)
        self.assertIsInstance(node(1)(0)(0), tree.html.String)

        self.assertString(node.name, 'ul')
        self.assertString(node(0).name, 'li')
        self.assertString(node(1).name, 'li')

        self.assertString(node(0)(0).name, 'p')
        self.assertString(node(1)(0).name, 'p')

        self.assertString(node(0)(0)(0).content, 'foo')
        self.assertString(node(1)(0)(0).content, 'bar')

    def testWrite(self):
        node = self.node(u'- foo\n- bar')
        self.assertString(node.write(), '<ul><li><p>foo </p></li><li><p>bar</p></li></ul>')

    def testNestedCode(self):
        node = self.node(u'- foo\n\n  ```language=text\n  code\n  ```')
        self.assertString(node.write(), '<ul><li><p>foo</p><pre><code ' \
                                        'class="language-text">\ncode\n</code></pre></li></ul>')


class TestRenderUnorderedListMaterialize(TestRenderUnorderedListHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)

    def testWrite(self):
        node = self.node(u'- foo\n- bar')
        self.assertString(node.write(),
                          '<ul class="browser-default"><li><p>foo </p></li><li><p>bar</p></li></ul>')

    def testNestedCode(self):
        node = self.node(u'- foo\n\n  ```language=text\n  code\n  ```')
        self.assertString(node.write(), '<ul class="browser-default"><li><p>foo</p><pre><code ' \
                                        'class="language-text">\ncode\n</code></pre></li></ul>')

class TestRenderUnorderedListLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testTree(self):
        node = self.render(u'- foo\n- bar').find('document')(0)

        self.assertIsInstance(node, tree.latex.Environment)
        self.assertIsInstance(node(0), tree.latex.CustomCommand)
        self.assertIsInstance(node(1), tree.latex.Command)
        self.assertIsInstance(node(2), tree.latex.String)
        self.assertIsInstance(node(3), tree.latex.String)
        self.assertIsInstance(node(4), tree.latex.CustomCommand)
        self.assertIsInstance(node(5), tree.latex.Command)
        self.assertIsInstance(node(6), tree.latex.String)

        self.assertString(node.name, 'itemize')
        self.assertString(node(0).name, 'item')
        self.assertString(node(1).name, 'par')
        self.assertString(node(2).content, 'foo')
        self.assertString(node(3).content, ' ')
        self.assertString(node(4).name, 'item')
        self.assertString(node(5).name, 'par')
        self.assertString(node(6).content, 'bar')

    def testWrite(self):
        node = self.render(u'- foo\n- bar').find('document')(0)
        self.assertString(node.write(),
                          '\n\\begin{itemize}\n\n\\item\n\\par\nfoo \n\\item\n\\par\nbar\n\\end{itemize}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
