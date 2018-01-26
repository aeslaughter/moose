#!/usr/bin/env python
"""
Tests for Lexer objects.
"""
import re
import unittest
from moosedown.base import lexers
from moosedown.common import exceptions

class TestLexerInformation(unittest.TestCase):
    """
    Test Lexer base class and associated objects.
    """
    def testGrammer(self):
        grammer = lexers.Grammer()

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add(1, [], [], [])
        self.assertIn("'name' must be of type", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', 1, [], [])
        self.assertIn("'regex' must be of type", e.exception.message)

        #TODO: Perform this check
        """
        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', re.compile(''), 1, [])
        self.assertIn("'function' must be of type", e.exception.message)
        """

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', re.compile(''), len, [])
        self.assertIn("'location' must be of type", e.exception.message)



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
    """

if __name__ == '__main__':
    unittest.main(verbosity=2)
