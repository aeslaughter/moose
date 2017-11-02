#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown import tree
from moosedown.base import testing

class TestCode(testing.MarkdownTestCase):
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
