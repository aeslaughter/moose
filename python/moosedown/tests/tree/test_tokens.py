#!/usr/bin/env python
import unittest
import logging
import inspect
import mock

from moosedown.tree import tokens

class TestTokens(unittest.TestCase):

    def testCoverage(self):
        status = []
        msg = "The following classes in tokens module do not have a required test.\n"
        for name, obj in inspect.getmembers(tokens):
            if inspect.isclass(obj):
                status.append(hasattr(self, 'test' + obj.__name__))
                if not status[-1]:
                    msg += '    {}\n'.format(obj.__name__)
        self.assertTrue(all(status), msg)

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
        with self.assertRaises(IOError) as e:
            token = tokens.Link()
        self.assertIn("The property 'url' is required.", e.exception.message)

        token = tokens.Link(url='foo')
        self.assertEqual(token.url, 'foo')
        token.url = 'bar'
        self.assertEqual(token.url, 'bar')

        with self.assertRaises(TypeError) as e:
            token.url = 42
        gold = "The supplied property 'url' must be of type 'str', but 'int' was provided."
        self.assertEqual(e.exception.message, gold)

    def testShortcut(self):
        with self.assertRaises(IOError) as e:
            token = tokens.Shortcut(key='foo')
        self.assertEqual("The property 'content' is required.", e.exception.message)
        with self.assertRaises(IOError) as e:
            token = tokens.Shortcut(content='foo')
        self.assertEqual("The property 'key' is required.", e.exception.message)

        token = tokens.Shortcut(key='key', content='content')
        self.assertEqual(token.key, 'key')
        self.assertEqual(token.content, 'content')

    def testShortcutLink(self):
        with self.assertRaises(IOError) as e:
            token = tokens.ShortcutLink()
        self.assertEqual("The property 'key' is required.", e.exception.message)

        token = tokens.ShortcutLink(key='key')
        self.assertEqual(token.key, 'key')

    def testInlineCode(self):
        with self.assertRaises(IOError) as e:
            token = tokens.InlineCode()
        self.assertIn("The property 'code' is required.", e.exception.message)
        token = tokens.InlineCode(code='int x;')
        self.assertEqual(token.code, 'int x;')

    def testStrong(self):
        token = tokens.Strong()

    def testEmphasis(self):
        token = tokens.Emphasis()

    def testUnderline(self):
        token = tokens.Underline()

    def testStrikethrough(self):
        token = tokens.Strikethrough()

    def testQuote(self):
        token = tokens.Quote()

    def testSuperscript(self):
        token = tokens.Superscript()

    def testSubscript(self):
        token = tokens.Subscript()


if __name__ == '__main__':
    unittest.main(verbosity=2)
