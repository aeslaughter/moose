#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestRenderLabelHTML(testing.MooseDocsTestCase):
    def testWrite(self):
        node = tree.tokens.Label(None, text=u'foo')
        html = self.write(node)
        self.assertEqual(html, '')

class TestRenderLabelMaterialize(TestRenderLabelHTML):
    RENDERER = MaterializeRenderer

class TestRenderLabelLatex(testing.MooseDocsTestCase):
    RENDERER = LatexRenderer

    def testWrite(self):
        node = self.render(tree.tokens.Label(None, text=u'foo')).find('document')(-1)
        tex = self.write(node)
        self.assertString(tex, '\\label{foo}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
