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


if __name__ == '__main__':
    unittest.main(verbosity=2)
