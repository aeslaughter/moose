#!/usr/bin/env python
"""Testing for moosedown.extensions.core MooseDocs extension."""
import unittest
import mock
import moosedown
from moosedown.extensions import core
from moosedown.tree import tokens, html, latex
from moosedown.base import testing, renderers

# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    """Test Token object for <EXTENSION> MooseDocs extension."""
    # There are no tokens defined in teh core, but in the future thier might. Having this empty
    # test will produce a usefull error from the integrety tests.

# TOKENIZE TESTS
class TestBreakTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Break"""
    def testToken(self):
        node = self.ast(u'foo\nbar')(0)
        self.assertIsInstance(node, tokens.Paragraph)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Break)
        self.assertIsInstance(node(2), tokens.Word)
        self.assertEqual(node(1).content, '\n')
        self.assertEqual(node(1).count, 1)

class TestCodeTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Code"""
    def testToken(self):
        code = self.ast(u'```\nint x;\n```')(0)
        self.assertIsInstance(code, tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'text')

    def testLanguage(self):
        code = self.ast(u'```language=cpp\nint x;\n```')(0)
        self.assertIsInstance(code, tokens.Code)
        self.assertString(code.code, '\nint x;\n')
        self.assertString(code.language, 'cpp')

class TestEndOfFileTokenize(testing.MooseDocsTestCase):
    """Test tokenization of EndOfFile"""
    def testToken(self):
        # TODO:As far as I can tell the core.EndOfFile component is not reachable, if a way to reach
        # it found then it needs to get added to this test.
        ast = self.ast(u'foo\n     ')(0)
        self.assertIsInstance(ast, tokens.Paragraph)

class TestFormatTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Format"""
    def testStrong(self):
        ast = self.ast(u'+strong+')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")

        ast = self.ast(u'+strong with space\nand a new line+')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strong")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testUnderline(self):
        ast = self.ast(u'=underline=')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")

        ast = self.ast(u'=underline with space\nand a new line=')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "underline")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testEmphasis(self):
        ast = self.ast(u'*emphasis*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")

        ast = self.ast(u'*emphasis with space\nand a new line*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "emphasis")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testStrikethrough(self):
        ast = self.ast(u'~strikethrough~')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")

        ast = self.ast(u'~strikethrough with space\nand a new line~')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Strikethrough)
        self.assertIsInstance(ast(0)(0)(0), tokens.String)
        self.assertEqual(ast(0)(0)(0).content, "strikethrough")
        self.assertEqual(ast(0)(0)(-1).content, "line")

    def testSubscript(self):
        ast = self.ast(u'S_x_')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1), tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testSuperscript(self):
        ast = self.ast(u'S^x^')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1), tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tokens.Word)
        self.assertEqual(ast(0)(1)(0).content, "x")

    def testMonospace(self):
        ast = self.ast(u'`x`')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Monospace)
        self.assertEqual(ast(0)(0).code, "x")

        ast = self.ast(u'`*x*`')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Monospace)
        self.assertEqual(ast(0)(0).code, u"*x*")

    def testSuperscriptAndSubscript(self):
        ast = self.ast(u's_y^x^_')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1), tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

        ast = self.ast(u's^y_x_^')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1), tokens.Superscript)
        self.assertIsInstance(ast(0)(1)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1)(1), tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(1)(0), tokens.Word)
        self.assertEqual(ast(0)(1)(1)(0).content, "x")

    def testNesting(self):
        ast = self.ast(u'=*emphasis* underline=')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0)(0), tokens.Word)
        self.assertEqual(ast(0)(0)(0)(0).content, "emphasis")
        self.assertIsInstance(ast(0)(0)(2), tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "underline")

        ast = self.ast(u'*=underline= emphasis*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.Underline)
        self.assertEqual(ast(0)(0)(0)(0).content, "underline")
        self.assertIsInstance(ast(0)(0)(2), tokens.Word)
        self.assertEqual(ast(0)(0)(2).content, "emphasis")

        ast = self.ast(u'*=+~strike~ bold+ under= emphasis*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0)(0), tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0)(0)(0), tokens.Strikethrough)

        ast = self.ast(u's_*emphasis*_')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(1), tokens.Subscript)
        self.assertIsInstance(ast(0)(1)(0), tokens.Emphasis)
        self.assertEqual(ast(0)(1)(0)(0).content, "emphasis")

        ast = self.ast(u'*s_x_*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.Word)
        self.assertIsInstance(ast(0)(0)(1), tokens.Subscript)
        self.assertEqual(ast(0)(0)(1)(0).content, "x")

class TestHeadingHashTokenize(testing.MooseDocsTestCase):
    """Test tokenization of HeadingHash"""
    def testToken(self):
        ast = self.ast(u'# Heading with Spaces')
        h = ast(0)
        self.assertIsInstance(h, tokens.Heading)
        self.assertEqual(h.level, 1)
        self.assertIsInstance(h(0), tokens.Label)
        self.assertIsInstance(h(1), tokens.Word)
        self.assertIsInstance(h(2), tokens.Space)
        self.assertIsInstance(h(3), tokens.Word)
        self.assertIsInstance(h(4), tokens.Space)
        self.assertIsInstance(h(5), tokens.Word)
        self.assertEqual(h(1).content, 'Heading')
        self.assertEqual(h(3).content, 'with')
        self.assertEqual(h(5).content, 'Spaces')

    def testLevels(self):
        for i in range(1,7):
            ast = self.ast(u'{} Heading'.format('#'*i))
            self.assertEqual(ast(0).level, i)

class TestLinkTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Link"""
    def testToken(self):
        link = self.ast(u'[link](url.html)')(0)(0)
        self.assertIsInstance(link.parent, tokens.Paragraph)
        self.assertIsInstance(link, tokens.Link)
        self.assertIsInstance(link(0), tokens.Word)
        self.assertEqual(link(0).content, 'link')
        self.assertEqual(link.url, 'url.html')

    def testSettings(self):
        link = self.ast(u'[link](url.html id=bar)')(0)(0)
        self.assertEqual(link['id'], 'bar')

class TestListTokenize(testing.MooseDocsTestCase):
    """Test tokenization of List"""
    # Base class that is not used directly.

class TestNumberTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Number"""
    def testToken(self):
        node = self.ast(u'foo1bar')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Number)
        self.assertIsInstance(node(2), tokens.Word)

class TestOrderedListTokenize(testing.MooseDocsTestCase):
    """Test tokenization of OrderedList"""
    def testToken(self):
        token = self.ast(u'1. foo\n1. bar')
        self.assertIsInstance(token(0), tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(0)(1), tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tokens.Word)

    def testStart(self):
        token = self.ast(u'42. foo\n1. bar')
        self.assertIsInstance(token(0), tokens.OrderedList)
        self.assertEqual(token(0).start, 42)

    def testSeparate(self):
        token = self.ast(u'1. foo\n\n\n1. bar')
        self.assertIsInstance(token(0), tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(1), tokens.OrderedList)
        self.assertIsInstance(token(1)(0), tokens.ListItem)
        self.assertIsInstance(token(1)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(1)(0)(0)(0), tokens.Word)

    def testNesting(self):
        token = self.ast(u'1. foo\n\n   - nested\n   - list\n1. bar')
        self.assertIsInstance(token(0), tokens.OrderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(0)(0)(1), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0)(1)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(1)(1), tokens.ListItem)

        self.assertIsInstance(token(0)(1), tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tokens.Word)

class TestParagraphTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Paragraph"""
    def testToken(self):
        for i in range(2, 5):
            token = self.ast(u'foo{}bar'.format('\n'*i))
            self.assertIsInstance(token(0), tokens.Paragraph)
            self.assertIsInstance(token(0)(0), tokens.Word)

            self.assertIsInstance(token(1), tokens.Paragraph)
            self.assertIsInstance(token(1)(0), tokens.Word)

class TestPunctuationTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Punctuation"""
    def testToken(self):
        node = self.ast(u'a-z')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Punctuation)
        self.assertIsInstance(node(2), tokens.Word)

        self.assertString(node(1).content, '-')

    def testMultiple(self):
        node = self.ast(u'a-$#%z')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Punctuation)
        self.assertIsInstance(node(2), tokens.Word)
        self.assertString(node(1).content, '-$#%')

    def testCaret(self):
        node = self.ast(u'a^z')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Punctuation)
        self.assertIsInstance(node(2), tokens.Word)
        self.assertString(node(1).content, '^')

    def testAll(self):
        node = self.ast(u'Word!@#$%^&*()-=_+{}[]|\":;\'?/>.<,~`   Word')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Punctuation)
        self.assertIsInstance(node(2), tokens.Space)
        self.assertIsInstance(node(3), tokens.Word)
        self.assertString(node(1).content, '!@#$%^&*()-=_+{}[]|\":;\'?/>.<,~`')

class TestQuoteTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Quote"""
    def testToken(self):
        node = self.ast(u'> foo bar')(0)
        self.assertIsInstance(node, tokens.Quote)
        self.assertIsInstance(node(0), tokens.Paragraph)
        self.assertIsInstance(node(0)(0), tokens.Word)
        self.assertIsInstance(node(0)(1), tokens.Space)
        self.assertIsInstance(node(0)(2), tokens.Word)

        self.assertString(node(0)(0).content, 'foo')
        self.assertString(node(0)(1).content, ' ')
        self.assertString(node(0)(2).content, 'bar')

class TestShortcutTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Shortcut"""
    def testToken(self):
        shortcut = self.ast(u'[key]: this is the shortcut content')(0)
        self.assertIsInstance(shortcut, tokens.Shortcut)
        self.assertEqual(shortcut.key, 'key')
        self.assertEqual(shortcut.link, 'this is the shortcut content')

class TestShortcutLinkTokenize(testing.MooseDocsTestCase):
    """Test tokenization of ShortcutLink"""
    def testToken(self):
        link = self.ast(u'[key]\n\n[key]: content')(0)(0)
        self.assertIsInstance(link, tokens.ShortcutLink)
        self.assertEqual(link.key, 'key')

class TestSpaceTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Space"""
    def testToken(self):
        node = self.ast(u'sit      amet')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Space)
        self.assertIsInstance(node(2), tokens.Word)

        self.assertString(node(0).content, 'sit')
        self.assertString(node(1).content, ' ')
        self.assertEqual(node(1).count, 6)
        self.assertString(node(2).content, 'amet')

class TestUnorderedListTokenize(testing.MooseDocsTestCase):
    """Test tokenization of UnorderedList"""
    def testToken(self):
        token = self.ast(u'- foo\n- bar')
        self.assertIsInstance(token(0), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(0)(1), tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tokens.Word)

    def testSeparate(self):
        token = self.ast(u'- foo\n\n\n- bar')
        self.assertIsInstance(token(0), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(1), tokens.UnorderedList)
        self.assertIsInstance(token(1)(0), tokens.ListItem)
        self.assertIsInstance(token(1)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(1)(0)(0)(0), tokens.Word)

    def testNesting(self):
        token = self.ast(u'- foo\n\n  - nested\n  - list\n- bar')
        self.assertIsInstance(token(0), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(0)(0), tokens.Word)

        self.assertIsInstance(token(0)(0)(1), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0)(1)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(1)(1), tokens.ListItem)

        self.assertIsInstance(token(0)(1), tokens.ListItem)
        self.assertIsInstance(token(0)(1)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(1)(0)(0), tokens.Word)

    def testNestedCode(self):
        token = self.ast(u'- foo\n\n  ```\n  bar\n  ```')
        self.assertIsInstance(token(0), tokens.UnorderedList)
        self.assertIsInstance(token(0)(0), tokens.ListItem)
        self.assertIsInstance(token(0)(0)(0), tokens.Paragraph)
        self.assertIsInstance(token(0)(0)(1), tokens.Code)

class TestWordTokenize(testing.MooseDocsTestCase):
    """Test tokenization of Word"""
    def testToken(self):
        node = self.ast(u'sit amet, consectetur')(0)
        self.assertIsInstance(node(0), tokens.Word)
        self.assertIsInstance(node(1), tokens.Space)
        self.assertIsInstance(node(2), tokens.Word)
        self.assertIsInstance(node(3), tokens.Punctuation)
        self.assertIsInstance(node(4), tokens.Space)
        self.assertIsInstance(node(5), tokens.Word)

        self.assertString(node(0).content, 'sit')
        self.assertString(node(2).content, 'amet')
        self.assertString(node(3).content, ',')
        self.assertString(node(5).content, 'consectetur')

# RENDERER TESTS
class TestRenderBreakHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderBreak with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'foo\nbar'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)

    def testTree(self):
        node = self.node()
        self.assertIsInstance(node, html.Tag)
        self.assertIsInstance(node(0), html.String)
        self.assertIsInstance(node(1), html.String)
        self.assertIsInstance(node(2), html.String)

        self.assertString(node(0).content, 'foo')
        self.assertString(node(1).content, u' ')
        self.assertString(node(2).content, 'bar')

    def testWrite(self):
        node = self.node()
        html = node.write()
        self.assertString(html, '<p>foo bar</p>')

class TestRenderBreakMaterialize(TestRenderBreakHTML):
    """Test renderering of RenderBreak with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderBreakLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderBreak with LatexRenderer"""

    RENDERER = renderers.LatexRenderer

    def testTree(self):
        node = self.render(u'foo\nbar')(-1)
        self.assertIsInstance(node, latex.Environment)
        self.assertIsInstance(node(0), latex.CustomCommand)
        self.assertIsInstance(node(1), latex.String)
        self.assertIsInstance(node(2), latex.String)
        self.assertIsInstance(node(3), latex.String)

        self.assertString(node(0).name, 'par')
        self.assertString(node(1).content, 'foo')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'bar')

    def testWrite(self):
        node = self.render(u'foo\nbar')(-1)
        tex = node.write()
        self.assertString(tex, '\n\\begin{document}\n\n\\par\nfoo bar\n\\end{document}\n')

class TestRenderCodeHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderCode with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer

    def testTree(self):
        node = self.render(u'```\nint x;\n```').find('pre')
        self.assertIsInstance(node, html.Tag)
        self.assertIsInstance(node(0), html.Tag)
        self.assertIsInstance(node(0)(0), html.String)

        self.assertEqual(node.name, 'pre')
        self.assertEqual(node(0).name, 'code')
        self.assertString(node(0)['class'], 'language-text')
        self.assertString(node(0)(0).content, '\nint x;\n')

    def testWrite(self):
        node = self.render(u'```\nint x;\n```').find('pre')
        self.assertString(node.write(), '<pre><code class="language-text">\nint x;\n</code></pre>')

    def testTreeLanguage(self):
        node = self.render(u'```language=cpp\nint x;\n```').find('pre')
        self.assertString(node(0)['class'], 'language-cpp')

    def testWriteLanguage(self):
        node = self.render(u'```language=cpp\nint x;\n```').find('pre')
        self.assertString(node.write(), '<pre><code class="language-cpp">\nint x;\n</code></pre>')

class TestRenderCodeMaterialize(TestRenderCodeHTML):
    """Test renderering of RenderCode with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderCodeLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderCode with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    @unittest.skip('TODO')
    def testTree(self):
        node = self.node()

    @unittest.skip('TODO')
    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderEmphasisHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderEmphasis with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'*content*'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)(0)

    def testTree(self):
        node = self.node()
        self.assertIsInstance(node, html.Tag)
        self.assertIsInstance(node(0), html.String)

        self.assertString(node.name, 'em')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.node()
        html = node.write()
        self.assertString(html, '<em>content</em>')

class TestRenderEmphasisMaterialize(TestRenderEmphasisHTML):
    """Test renderering of RenderEmphasis with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

class TestRenderEmphasisLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderEmphasis with LatexRenderer"""

    RENDERER = renderers.LatexRenderer

    def testTree(self):
        node = self.render(u'*content*')(-1)(1)

        self.assertIsInstance(node, latex.Command)
        self.assertIsInstance(node(0), latex.String)

        self.assertString(node.name, 'emph')
        self.assertString(node(0).content, 'content')

    def testWrite(self):
        node = self.render(u'*content*')(-1)(1)
        tex = node.write()
        self.assertString(tex, '\\emph{content}')

class TestRenderExceptionHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderException with HTMLRenderer"""
    EXTENSIONS = [moosedown.extensions.core, moosedown.extensions.command]
    RENDERER = renderers.HTMLRenderer
    TEXT = u'!unknown command'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)

    @mock.patch('logging.Logger.error')
    def testTree(self, mock):
        node = self.node()
        self.assertIsInstance(node, html.Tag)
        self.assertIsInstance(node(0), html.String)
        mock.assert_called_once()

    @mock.patch('logging.Logger.error')
    def testWrite(self, mock):
        node = self.node()
        self.assertString(node.write(), '<div class="moose-exception">!unknown command</div>')

class TestRenderExceptionMaterialize(TestRenderExceptionHTML):
    """Test renderering of RenderException with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testWrite(self):
        node = self.node()
        self.assertIn('class="moose-exception modal-trigger">!unknown command</a>', node.write())

class TestRenderExceptionLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderException with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'!unknown command'

    def node(self):
        return self.render(self.TEXT).find('document')

    @mock.patch('logging.Logger.error')
    def testTree(self, mock):
        node = self.render(u'!unknown command').find('document')
        self.assertString(node(1).content, '!')
        self.assertString(node(2).content, 'unknown')
        self.assertString(node(3).content, ' ')
        self.assertString(node(4).content, 'command')

    @mock.patch('logging.Logger.error')
    def testWrite(self, mock):
        node = self.render(u'!unknown command').find('document')
        self.assertString(node.write(), '\n\\begin{document}\n\n\\par\n!unknown command\n\\end{document}\n')

class TestRenderHeadingHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderHeading with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer

    def node(self, content):
        return self.render(content).find('moose-content', attr='class')(0)

    def testTree(self):
        h = self.node(u'# Heading with Spaces')
        self.assertIsInstance(h, html.Tag)
        self.assertEqual(h.name, 'h1')
        for child in h.children:
            self.assertIsInstance(child, html.String)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(1).content, ' ')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(3).content, ' ')
        self.assertEqual(h(4).content, 'Spaces')

        self.assertString(h.write(), "<h1>Heading with Spaces</h1>")

    def testSettings(self):
        h = self.node(u'# Heading with Spaces style=font-size:42pt;')
        self.assertIsInstance(h, html.Tag)
        self.assertEqual(h.name, 'h1')
        for child in h.children:
            self.assertIsInstance(child, html.String)
        self.assertEqual(h(0).content, 'Heading')
        self.assertEqual(h(1).content, ' ')
        self.assertEqual(h(2).content, 'with')
        self.assertEqual(h(3).content, ' ')
        self.assertEqual(h(4).content, 'Spaces')
        self.assertEqual(h.style, {'font-size':'42pt'})

        self.assertString(h.write(), '<h1 style="font-size:42pt;">Heading with Spaces</h1>')

class TestRenderHeadingMaterialize(TestRenderHeadingHTML):
    """Test renderering of RenderHeading with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def node(self, text):
        return self.render(text).find('moose-content', attr='class')(0)(0)


class TestRenderHeadingLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderHeading with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def checkLevel(self, lvl, cmd):
        node = self.render(u'{} Heading with Space'.format('#'*lvl))(-1)(0)
        self.assertIsInstance(node, latex.Command)
        self.assertString(node.name, cmd)

        self.assertIsInstance(node(0), latex.Command)
        self.assertString(node(0).name, 'label')
        self.assertString(node(0)(0).content, 'heading-with-space')

        self.assertIsInstance(node(1), latex.String)
        self.assertIsInstance(node(2), latex.String)
        self.assertIsInstance(node(3), latex.String)
        self.assertIsInstance(node(4), latex.String)
        self.assertIsInstance(node(5), latex.String)

       # self.assertString(node(0).name, 'par')
        self.assertString(node(1).content, 'Heading')
        self.assertString(node(2).content, ' ')
        self.assertString(node(3).content, 'with')
        self.assertString(node(4).content, ' ')
        self.assertString(node(5).content, 'Space')

        tex = node.write()
        self.assertString(tex, '\n\\%s{\\label{heading-with-space}Heading with Space}\n' % cmd)

    def testLevels(self):
        self.checkLevel(1, 'chapter')
        self.checkLevel(2, 'section')
        self.checkLevel(3, 'subsection')
        self.checkLevel(4, 'subsubsection')
        self.checkLevel(5, 'paragraph')
        self.checkLevel(6, 'subparagraph')

class TestRenderLabelHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderLabel with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderLabelMaterialize(TestRenderLabelHTML):
    """Test renderering of RenderLabel with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderLabelLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderLabel with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderLinkHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderLink with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderLinkMaterialize(TestRenderLinkHTML):
    """Test renderering of RenderLink with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderLinkLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderLink with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderListItemHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderListItem with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderListItemMaterialize(TestRenderListItemHTML):
    """Test renderering of RenderListItem with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderListItemLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderListItem with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderMonospaceHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderMonospace with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderMonospaceMaterialize(TestRenderMonospaceHTML):
    """Test renderering of RenderMonospace with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderMonospaceLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderMonospace with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderOrderedListHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderOrderedList with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderOrderedListMaterialize(TestRenderOrderedListHTML):
    """Test renderering of RenderOrderedList with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderOrderedListLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderOrderedList with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderParagraphHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderParagraph with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderParagraphMaterialize(TestRenderParagraphHTML):
    """Test renderering of RenderParagraph with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderParagraphLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderParagraph with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderPunctuationHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderPunctuation with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderPunctuationMaterialize(TestRenderPunctuationHTML):
    """Test renderering of RenderPunctuation with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderPunctuationLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderPunctuation with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderQuoteHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderQuote with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderQuoteMaterialize(TestRenderQuoteHTML):
    """Test renderering of RenderQuote with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderQuoteLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderQuote with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderShortcutLinkHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderShortcutLink with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderShortcutLinkMaterialize(TestRenderShortcutLinkHTML):
    """Test renderering of RenderShortcutLink with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderShortcutLinkLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderShortcutLink with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrikethroughHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderStrikethrough with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrikethroughMaterialize(TestRenderStrikethroughHTML):
    """Test renderering of RenderStrikethrough with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrikethroughLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderStrikethrough with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStringHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderString with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStringMaterialize(TestRenderStringHTML):
    """Test renderering of RenderString with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStringLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderString with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrongHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderStrong with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrongMaterialize(TestRenderStrongHTML):
    """Test renderering of RenderStrong with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderStrongLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderStrong with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSubscriptHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderSubscript with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSubscriptMaterialize(TestRenderSubscriptHTML):
    """Test renderering of RenderSubscript with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSubscriptLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderSubscript with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSuperscriptHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderSuperscript with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSuperscriptMaterialize(TestRenderSuperscriptHTML):
    """Test renderering of RenderSuperscript with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderSuperscriptLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderSuperscript with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnderlineHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderUnderline with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnderlineMaterialize(TestRenderUnderlineHTML):
    """Test renderering of RenderUnderline with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnderlineLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderUnderline with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnorderedListHTML(testing.MooseDocsTestCase):
    """Test renderering of RenderUnorderedList with HTMLRenderer"""

    RENDERER = renderers.HTMLRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnorderedListMaterialize(TestRenderUnorderedListHTML):
    """Test renderering of RenderUnorderedList with MaterializeRenderer"""

    RENDERER = renderers.MaterializeRenderer

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

class TestRenderUnorderedListLatex(testing.MooseDocsTestCase):
    """Test renderering of RenderUnorderedList with LatexRenderer"""

    RENDERER = renderers.LatexRenderer
    TEXT = u'ENTER TEXT HERE'

    def node(self):
        return self.render(self.TEXT).find('document')

    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()

if __name__ == '__main__':
    unittest.main(verbosity=2)
