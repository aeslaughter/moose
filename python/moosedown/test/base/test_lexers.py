#!/usr/bin/env python
"""
Tests for Lexer and related objects.
"""
import re
import unittest
from moosedown.base import lexers
from moosedown.common import exceptions

class Proxy(object):
    """
    Proxy class for Components.
    """
    def __call__(self, *args):
        pass

class TestGrammer(unittest.TestCase):
    """
    Test Grammer object.
    """
    def testGrammer(self):
        grammer = lexers.Grammer()

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add(1, [], [], [])
        self.assertIn("'name' must be of type", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', 1, [], [])
        self.assertIn("'regex' must be of type", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', re.compile(''), 1, [])
        self.assertIn("'function' must be callable", e.exception.message)

        with self.assertRaises(exceptions.MooseDocsException) as e:
            grammer.add('foo', re.compile(''), Proxy(), [])
        self.assertIn("'location' must be of type", e.exception.message)

    def testPatterns(self):
        """
        Test the multiple patterns can be added.

        NOTE: The underlying Storage object that the Grammer class uses is thoroughly tested
              in the test/common/test_Storage.py.
        """
        grammer = lexers.Grammer()
        grammer.add('foo', re.compile(''), Proxy())
        grammer.add('bar', re.compile(''), Proxy())
        patterns = list(grammer)
        self.assertEqual(grammer[0].name, 'foo')
        self.assertEqual(grammer[1].name, 'bar')
        self.assertEqual(grammer['foo'].name, 'foo')
        self.assertEqual(grammer['bar'].name, 'bar')

class TestLexerInformation(unittest.TestCase):
    """
    Test LexerInformation class that stores parsing data.
    """
    def test(self):
        regex = re.compile(r'(?P<key>foo)')
        match = regex.search('foo bar')

        pattern = lexers.Grammer.Pattern(name='name', regex=regex, function=Proxy())
        info = lexers.LexerInformation(match=match, pattern=pattern, line=42)
        self.assertEqual(info.line, 42)
        self.assertIs(info.pattern, pattern)
        self.assertEqual(info.keys(), ['key'])
        for key, value in info.iteritems():
            self.assertEqual(key, 'key')
            self.assertEqual(value, 'foo')
        self.assertIn('key', info)
        self.assertIn('line:42', str(info))

if __name__ == '__main__':
    unittest.main(verbosity=2)
