#!/usr/bin/env python
import unittest
import logging
import mock

import moosedown
from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderExceptionHTML(testing.MooseDocsTestCase):
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.command]
    def node(self, text):
        return self.render(text).find('body')(0)

    @mock.patch('logging.Logger.error')
    def testTree(self, mock):
        node = self.node(u'!unknown command')
        self.assertIsInstance(node, tree.html.Tag)
        self.assertIsInstance(node(0), tree.html.String)
        mock.assert_called_once()

    @mock.patch('logging.Logger.error')
    def testWrite(self, mock):
        node = self.node(u'!unknown command')
        self.assertString(node.write(), '<div class="moose-exception">!unknown command</div>')

class TestRenderExceptionMaterialize(TestRenderExceptionHTML):
    RENDERER = MaterializeRenderer
    def node(self, text):
        return self.render(text).find('body')(0)(0)(0)(0)

    @mock.patch('logging.Logger.error')
    def testWrite(self, mock):
        node = self.node(u'!unknown command')
        self.assertIn('class="moose-exception modal-trigger">!unknown command</a>', node.write())

class TestRenderExceptionLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    @mock.patch('logging.Logger.error')
    def testTree(self, mock):
        node = self.render(u'!unknown command').find('document')
        self.assertString(node(1).content, '!')
        self.assertString(node(2).content, 'unknown')
        self.assertString(node(3).content, ' ')
        self.assertString(node(4).content, 'command')

    @mock.patch('logging.Logger.error')
    def testWrite(self, mock):
        node = self.render(u'!unknown command').find('document')
        self.assertString(node.write(), '\n\\begin{document}\n\n\\par\n!unknown command\n\\end{document}\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
