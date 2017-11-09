#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing, MaterializeRenderer, LatexRenderer

class TestCodeTokenize(testing.MarkdownTestCase):
    """
    Test fenced code blocks
    """
    def testBasic(self):
        code = self.ast('```\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'text')

        html = self.html(code)
        self.assertString(html.write(),
                          '<body><pre><code class="language-text">\nint x;\n</code></pre></body>')

    def testLanguage(self):
        code = self.ast('```language=cpp\nint x;\n```')(0)
        self.assertIsInstance(code, tree.tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'cpp')

        html = self.html(code)
        self.assertString(html.write(),
                         '<body><pre><code class="language-cpp">\nint x;\n</code></pre></body>')

class TestCodeHTML(testing.MarkdownTestCase):
    def testBasic(self):
        html = self.html('```\nint x;\n```').find('pre')
        self.assertString(html.write(),
                          '<pre><code class="language-text">\nint x;\n</code></pre>')

    def testLanguage(self):
        html = self.html('```language=cpp\nint x;\n```').find('pre')
        self.assertString(html.write(),
                          '<pre><code class="language-cpp">\nint x;\n</code></pre>')

class TestCodeMaterialize(TestCodeHTML):
    RENDERER = MaterializeRenderer


if __name__ == '__main__':
    unittest.main(verbosity=2)
