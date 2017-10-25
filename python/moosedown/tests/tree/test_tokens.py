#!/usr/bin/env python
import unittest
import logging
import mock

from moosedown.tree import tokens

class TestTokens(unittest.TestCase):

    @mock.patch('logging.Logger.error')
    def testToken(self, mock):
        token = tokens.Token()
        self.assertEqual(token.name, 'Token')
        self.assertEqual(token.line, None)
        token.line = 42
        self.assertEqual(token.line, 42)

        token.line = "42"
        mock.assert_called_once()
        args, _ = mock.call_args
        self.assertIn('must be of type "int"', args[0])

    def testString(self):
        token = tokens.String(content="content")
        self.assertEqual(token.content, "content")

        with self.assertRaises(TypeError) as e:
            token = tokens.String(content=1980)
        gold = "The supplied property 'content' must be of type 'str', but 'int' was provided."
        self.assertEqual(e.exception.message, gold)

    def testUnknown(self):
        token = tokens.Unknown(content="content")
        self.assertEqual(token.content, "content")

    def testWord(self):
        token = tokens.Word(content="content")
        self.assertEqual(token.content, "content")

    def testSpace(self):
        token = tokens.Space()
        self.assertEqual(token.content, ' ')
        self.assertEqual(token.count, 1)

        token = tokens.Space(count=42)
        self.assertEqual(token.content, ' ')
        self.assertEqual(token.count, 42)

        with self.assertRaises(TypeError) as e:
            token = tokens.Space(count='not int')
        gold = "The supplied property 'count' must be of type 'int', but 'str' was provided."
        self.assertEqual(e.exception.message, gold)

    def testBreak(self):
        token = tokens.Break()
        self.assertEqual(token.content, '\n')
        self.assertEqual(token.count, 1)

        token = tokens.Break(count=42)
        self.assertEqual(token.content, '\n')
        self.assertEqual(token.count, 42)

        with self.assertRaises(TypeError) as e:
            token = tokens.Space(count='not int')
        gold = "The supplied property 'count' must be of type 'int', but 'str' was provided."
        self.assertEqual(e.exception.message, gold)

    def testPunctuation(self):
        token = tokens.Punctuation(content='---')
        self.assertEqual(token.content, '---')

    def testNumber(self):
        token = tokens.Punctuation(content='1980')
        self.assertEqual(token.content, '1980')

    def testCode(self):
        token = tokens.Code(content="x+y=2;")
        self.assertEqual(token.content, "x+y=2;")

    def testHeading(self):
        token = tokens.Heading(level=4)
        self.assertEqual(token.level, 4)

        with self.assertRaises(TypeError) as e:
            token = tokens.Heading(level='not int')
        gold = "The supplied property 'level' must be of type 'int', but 'str' was provided."
        self.assertEqual(e.exception.message, gold)

    def testParagraph(self):
        token = tokens.Paragraph()

    def testUnorderedList(self):
        token = tokens.UnorderedList()

    def testOrderedList(self):
        token = tokens.OrderedList()
        self.assertEqual(token.start, 1)
        token = tokens.OrderedList(start=1980)
        self.assertEqual(token.start, 1980)

        with self.assertRaises(TypeError) as e:
            token = tokens.OrderedList(start='not int')
        gold = "The supplied property 'start' must be of type 'int', but 'str' was provided."
        self.assertEqual(e.exception.message, gold)

    def testListItem(self):
        with self.assertRaises(IOError) as e:
            token = tokens.ListItem()
        self.assertIn("A 'ListItem' must have a 'OrderedList' or 'UnorderedList' parent.",
                      e.exception.message)

        root = tokens.OrderedList()
        token = tokens.ListItem(parent=root)
        self.assertIs(token.parent, root)

    def testLink(self):
        pass



if __name__ == '__main__':
    unittest.main(verbosity=2)
