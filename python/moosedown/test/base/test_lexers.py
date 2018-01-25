#!/usr/bin/env python
"""
Tests for Lexer objects.
"""
import re
import unittest
from moosedown.base import lexers

class TestLexerInformation(unittest.TestCase):
    """
    Test Lexer base class.
    """
    def test(self):
        text = 'foo bar'
        regex = re.compile(r'foo')
        match = regex.search(text)
        def func():
            pass

        print dir(lexers)

        pattern = lexers.Grammer.Pattern(name='name', regex=regex, function=func)
        info = lexers.LexerInformation(match=match, pattern=pattern, line=42)
        print info


if __name__ == '__main__':
    unittest.main(verbosity=2)
