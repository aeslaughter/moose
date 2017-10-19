#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import tokens

class TestTokens(unittest.TestCase):

    @mock.patch('logging.Logger.error')
    def testToken(self, mock):
        token = tokens.Token(None)
        self.assertEqual(token.name, 'Token')
        self.assertEqual(token.line, None)
        token.line = 42
        self.assertEqual(token.line, 42)

        token.line = "42"
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn('must be of type "int"', args[0])

    def testString(self):
        token = tokens.String(None, content="content")
        self.assertEqual(token.content, "content")

    def testUnknown(self):
        token = tokens.Unknown(None, content="content")
        self.assertEqual(token.content, "content")

    def testWord(self):
        token = tokens.Word(None, content="content")
        self.assertEqual(token.content, "content")

    def testSpace(self):
        token = tokens.Space(None)
        self.assertEqual(token.content, ' ')
        self.assertEqual(token.count, 1)

        token = tokens.Space(None, count=42)
        self.assertEqual(token.content, ' ')
        self.assertEqual(token.count, 42)

        with self.assertRaises(TypeError) as e:
            token = tokens.Space(None, count='not int')
        self.assertIn('The count must be an int', e.exception.message)

    def testBreak(self):
        token = tokens.Break(None)
        self.assertEqual(token.content, '\n')
        self.assertEqual(token.count, 1)

        token = tokens.Break(None, count=42)
        self.assertEqual(token.content, '\n')
        self.assertEqual(token.count, 42)

        with self.assertRaises(TypeError) as e:
            token = tokens.Space(None, count='not int')
        self.assertIn('The count must be an int', e.exception.message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
