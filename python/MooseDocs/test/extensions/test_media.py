#!/usr/bin/env python
"""Testing for MooseDocs.extensions.media MooseDocs extension."""
import unittest

import MooseDocs
from moosedown.extensions import core, command, floats, media
from MooseDocs.tree import tokens, html, latex
from moosedown.base import testing, renderers

# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    """Test Token object for MooseDocs.extensions.media MooseDocs extension."""

    EXTENSIONS = [core, command, floats, media]

    def testImage(self):
        tok = media.Image(src=u'foo')
        self.assertEqual(tok.src, u'foo')

    def testVideo(self):
        tok = media.Video(src=u'foo')
        self.assertEqual(tok.src, u'foo')
        self.assertTrue(tok.controls)
        self.assertTrue(tok.autoplay)
        self.assertTrue(tok.loop)

        tok = media.Video(src=u'foo', controls=False, autoplay=False, loop=False)
        self.assertEqual(tok.src, u'foo')
        self.assertFalse(tok.controls)
        self.assertFalse(tok.autoplay)
        self.assertFalse(tok.loop)

# TOKENIZE TESTS
class TestMediaCommandBaseTokenize(testing.MooseDocsTestCase):
    """Test tokenization of MediaCommandBase"""
    # Base class, no test needed

class TestVideoCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of VideoCommand"""

    EXTENSIONS = [core, command, floats, media]

    def testToken(self):
        ast = self.ast(u'!media inl_blue.png')
        self.assertFalse(True)

class TestImageCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of ImageCommand"""

    EXTENSIONS = [core, command, floats, media]

    def testToken(self):
        ast = self.ast(u'!media inl_blue.png')
        self.assertFalse(True)

# RENDERER TESTS
class TestRenderImageHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderImage with HTMLRenderer"""

    EXTENSIONS = [core, command, floats, media]
    RENDERER = renderers.HTMLRenderer
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")

class TestRenderImageMaterialize(TestRenderImageHTML):
    """Test renderering of RenderImage with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderImageLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderImage with LatexRenderer"""

    EXTENSIONS = [MooseDocs.extensions.core, MooseDocs.extensions.media]
    RENDERER = renderers.LatexRenderer
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('document')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")

class TestRenderVideoHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderVideo with HTMLRenderer"""

    EXTENSIONS = [MooseDocs.extensions.core, MooseDocs.extensions.media]
    RENDERER = renderers.HTMLRenderer
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")

class TestRenderVideoMaterialize(TestRenderVideoHTML):
    """Test renderering of RenderVideo with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderVideoLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderVideo with LatexRenderer"""

    EXTENSIONS = [MooseDocs.extensions.core, MooseDocs.extensions.media]
    RENDERER = renderers.LatexRenderer
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('document')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")

if __name__ == '__main__':
    unittest.main(verbosity=2)
