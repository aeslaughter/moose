#!/usr/bin/env python
"""Testing for moosedown.extensions.media MooseDocs extension."""
import unittest
from moosedown.extensions import media
from moosedown.tree import tokens
from moosedown.base import testing, renderers

# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    """Test Token object for <EXTENSION> MooseDocs extension."""

    def testImage(self):
        pass

    def testVideo(self):
        pass

# TOKENIZE TESTS
class TestImageCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of ImageCommand"""
    def testToken(self):
        pass

class TestMediaCommandBaseTokenize(testing.MooseDocsTestCase):
    """Test tokenization of MediaCommandBase"""
    def testToken(self):
        pass

class TestVideoCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of VideoCommand"""
    def testToken(self):
        pass

class TestImageCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of ImageCommand"""
    def testToken(self):
        pass

class TestMediaCommandBaseTokenize(testing.MooseDocsTestCase):
    """Test tokenization of MediaCommandBase"""
    def testToken(self):
        pass

class TestVideoCommandTokenize(testing.MooseDocsTestCase):
    """Test tokenization of VideoCommand"""
    def testToken(self):
        pass

# RENDERER TESTS
class TestRenderImageHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderImage with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderImageMaterialize(TestRenderImageHTML):
    """Test renderering of RenderImage with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderImageLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderImage with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderVideoHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderVideo with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderVideoMaterialize(TestRenderVideoHTML):
    """Test renderering of RenderVideo with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderVideoLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderVideo with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

if __name__ == '__main__':
    unittest.main(verbosity=2)
