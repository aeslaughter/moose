#!/usr/bin/env python
"""
Tests for the Renderer objects.
"""
import unittest
import logging
from moosedown.common import exceptions
from moosedown.tree import tokens, html
from moosedown.base import renderers
from moosedown.base import components

logging.basicConfig(level=logging.CRITICAL)

class ParComponent(components.RenderComponent):
    """Convert Paragraph token to html Tag"""
    def __init__(self, *args, **kwargs):
        components.RenderComponent.__init__(self, *args, **kwargs)
        self.count = 0
    def reinit(self):
        """Count calls"""
        self.count += 1
    def createHTML(self, token, parent):
        """HTML conversion"""
        return html.Tag(parent, 'p')

class StringComponent(components.RenderComponent):
    """Convert String token to html Tag"""
    def createHTML(self, token, parent):
        """HTML conversion"""
        return html.String(parent, content=token.content)

class BadComponent(components.RenderComponent):
    """Class for testing missing method."""
    pass

class TestRenderer(unittest.TestCase):
    """
    Test Renderer object, this is a abstract base so testing is limited.
    """
    def testErrors(self):
        """Test most basic construction."""
        renderer = renderers.Renderer()

        with self.assertRaises(exceptions.MooseDocsException) as e:
            renderer.add(tokens.Paragraph(), ParComponent())
        self.assertIn("The argument 'token'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            renderer.add(tokens.Paragraph, 'WRONG')
        self.assertIn("The argument 'component'", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            renderer.add(tokens.Paragraph, ParComponent())
        self.assertIn("The Reader class of type", e.exception.message)

class TestHTMLRenderer(unittest.TestCase):
    """
    Test HTML renderering.
    """
    def testMissingCompomentMethod(self):
        """Test missing createHTML method."""
        renderer = renderers.HTMLRenderer()

        with self.assertRaises(exceptions.MooseDocsException) as e:
            renderer.add(tokens.Paragraph, BadComponent())
        self.assertIn("does not have a createHTML method", e.exception.message)

    def testProcessException(self):
        """
        Test exception from a missing registration of token class.
        """
        renderer = renderers.HTMLRenderer()
        with self.assertRaises(exceptions.MooseDocsException) as e:
            renderer.process(html.Tag(None, 'div'), tokens.Token(None))
        self.assertIn("An error occured while rendering", e.exception.message)
        self.assertIn("execute the createHTML", e.exception.message)
        self.assertIn("tokens.Token", e.exception.message)

    def testReinit(self):
        """
        Test the component reinit method is called.
        """
        ast = tokens.Paragraph(None)
        comp = ParComponent()
        renderer = renderers.HTMLRenderer()
        renderer.add(tokens.Paragraph, comp)
        renderer.render(ast)
        renderer.render(ast)
        self.assertEqual(comp.count, 2)

    def testProcess(self):
        """
        Test Renderer.process method.
        """
        ast = tokens.Paragraph(None)
        tokens.String(ast, content=u'foo')

        renderer = renderers.HTMLRenderer()
        renderer.add(tokens.Paragraph, ParComponent())
        renderer.add(tokens.String, StringComponent())

        root = html.Tag(None, 'div')
        renderer.process(root, ast)
        self.assertIsInstance(root(0), html.Tag)
        self.assertEqual(root(0).name, 'p')
        self.assertIsInstance(root(0)(0), html.String)
        self.assertEqual(root(0)(0).content, u'foo')

    def testRender(self):
        """
        Test Renderer.render method.
        """
        ast = tokens.Paragraph(None)
        tokens.String(ast, content=u'foo')

        renderer = renderers.HTMLRenderer()
        renderer.add(tokens.Paragraph, ParComponent())
        renderer.add(tokens.String, StringComponent())

        root = renderer.render(ast)
        self.assertIsInstance(root, html.Tag)
        self.assertEqual(root.name, 'body')
        self.assertIsInstance(root(0), html.Tag)
        self.assertEqual(root(0).name, 'p')
        self.assertIsInstance(root(0)(0), html.String)
        self.assertEqual(root(0)(0).content, u'foo')


if __name__ == '__main__':
    unittest.main(verbosity=2)
