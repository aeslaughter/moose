#!/usr/bin/env python
import unittest
import logging
import mock

from MooseDocs.tree import tokens

class TestTokens(unittest.TestCase):

    def testRoot(self):
        token = tokens.Token(None)
        self.assertEqual(token.name, 'Token')
        self.assertEqual(token.line, None)

    def testLine(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
