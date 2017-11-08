"""
This defines the core Markdown translation to HTML and LaTeX.
"""
import re
import logging

import moosedown
from moosedown import base
from moosedown import common
from moosedown import tree

LOG = logging.getLogger(__name__)
SHORTCUT_DATABASE = dict()

def make_extension():
    """
    Create and return the MarkdownExtension and RenderExtension objects for the core extension.
    """
    return CoreMarkdownExtension(), CoreRenderExtension()

class CoreMarkdownExtension(base.MarkdownExtension):
    """
    The core markdown parser extension.

    This extension provides to core conversion from markdown syntax to an AST.
    """
    @staticmethod
    def getConfig():
        """
        The default configuration options.
        """
        config = base.MarkdownExtension.getConfig()
        return config

    def extend(self):
        """
        Add the extension components.
        """

        # Block
        self.addBlock(Code())
        self.addBlock(Quote())
        self.addBlock(HeadingHash())
        self.addBlock(OrderedList())
        self.addBlock(UnorderedList())
        self.addBlock(Shortcut())
        self.addBlock(Command())
        self.addBlock(Paragraph())
        self.addBlock(Break())

        # Inline
        self.addInline(Backtick())
        self.addInline(Format())
        self.addInline(Link())
        self.addInline(ShortcutLink())
        self.addInline(Punctuation())
        self.addInline(Number())
        self.addInline(Word())
        self.addInline(Break())
        self.addInline(Space())

class MarkdownComponent(base.TokenComponent):
    """
    Base Markdown component which defines the typically html tag settings and a means to apply them.
    """
    @staticmethod
    def defaultSettings():
        settings = base.TokenComponent.defaultSettings()
        settings['style'] = ('', "The style settings that are passed to the HTML flags.")
        settings['class'] = ('', "The class settings to be passed to the HTML flags.")
        settings['id'] = ('', "The class settings to be passed to the HTML flags.")
        return settings

    @property
    def attributes(self):
        """
        Return a dictionary with the common html settings.
        """
        return {'style':self.settings['style'], 'id':self.settings['id'], 'class':self.settings['class']}

class Command(MarkdownComponent):
    """
    Provides a component for creating commands.

    A command is defined by an exclamation mark followed by a keyword and optionally a sub-command.

    This allows all similar patterns to be handled by a single regex, which should aid in parsing
    speed as well as reduce the burden of adding new commands.

    New commands are added by creating a CommandComponent object and adding this component to the
    MarkdownExtension via the addCommand method (see extensions/devel.py for an example).
    """
    RE = re.compile('!(?P<command>\w+)\s(?P<subcommand>\w+)(?P<settings>.*?$)?(?P<content>.*?)\n{2,}|\Z',
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        cmd = (match.group('command'), match.group('subcommand'))

        #TODO: Error check
        if cmd not in base.MarkdownExtension.__COMMANDS__:
            return tree.tokens.String(parent, match.group())

        obj = base.MarkdownExtension.__COMMANDS__[cmd]
        obj.settings = self.settings
        obj.line = self.line
        token = obj.createToken(match, parent)
        return token

class Code(MarkdownComponent):
    """
    Fenced code blocks.
    """
    RE = re.compile(r'\s*`{3}(?P<settings>.*?)$(?P<code>.*?)`{3}',
                    flags=re.MULTILINE|re.DOTALL)

    @staticmethod
    def defaultSettings():
        settings = MarkdownComponent.defaultSettings()
        settings['language'] = ('text', "The code language to use for highlighting.")
        return settings

    def createToken(self, match, parent):
        return tree.tokens.Code(parent, code=match.group('code'),
                                language=self.settings['language'], **self.attributes)

class HeadingHash(MarkdownComponent):
    """
    Hash style markdown headings with settings.

    # Heading Level One with=settings
    """
    TOKEN = tree.tokens.Heading
    RE = re.compile(r'\s*(?P<level>#{1,6})\s'    # match 1 to 6 #'s at the beginning of line
                    r'(?P<inline>.*?)'           # heading text that will be inline parsed
                    r'(?P<settings>\s+\w+=.*?)?' # optional match key, value settings
                    r'(?:\Z|\n+)',               # match up to end of string or newline(s)
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        return tree.tokens.Heading(parent, level=match.group('level').count('#'), **self.attributes)

class Link(MarkdownComponent):
    """
    Markdown links [foo](bar with=settings)
    """
    RE = re.compile(r'\[(?P<inline>.*?)\]'         # link text
                    r'\((?P<url>.*?)'              # link url
                    r'(?:\s+(?P<settings>.*?))?\)' # settings
                    )

    def createToken(self, match, parent):
        return tree.tokens.Link(parent, url=match.group('url'), **self.attributes)


class Shortcut(MarkdownComponent):
    """
    Markdown shortcuts.

    [foo]: something or another
    """
    RE = re.compile(r'\s*\[(?P<key>.*?)\]:\s'  # shortcut key
                    r'(?P<content>.*?)'        # shortcut value
                    r'(?:\n+|\Z)',             # stop new line or end of file
                    flags=re.MULTILINE)

    def createToken(self, match, parent):
        token = tree.tokens.Shortcut(parent, key=match.group('key'), content=match.group('content'))
        SHORTCUT_DATABASE[token.key] = token.content
        return token

class ShortcutLink(MarkdownComponent):
    """
    Markdown shortcut use.
    """
    RE = re.compile(r'\[(?P<key>.*?)\]')
    def createToken(self, match, parent):
        return tree.tokens.ShortcutLink(parent, key=match.group('key'))

class String(MarkdownComponent):
    """
    Base token for strings (i.e., words, numbers, etc.), this is
    """
    def createToken(self, match, parent):
        return token.String(parent, content=match.group())

class Break(String):
    """
    Line breaks.
    """
    RE = re.compile(r'(?P<break>\n+)')
    def createToken(self, match, parent):
        return tree.tokens.Break(parent, count=len(match.group('break')))

class Space(String):
    """
    Spaces.
    """
    RE = re.compile(r'(?P<space> +)')
    def createToken(self, match, parent):
        return tree.tokens.Space(parent, count=len(match.group('space')))

class Punctuation(String):
    """
    Not letters, numbers, or spaces.
    """
    RE = re.compile(r'([^A-Z|^a-z|^0-9|^\s]+)')
    def createToken(self, match, parent):
        return tree.tokens.Punctuation(parent, content=match.group())

class Number(String):
    """
    Numbers.
    """
    RE = re.compile(r'([0-9]+)')
    def createToken(self, match, parent):
        return tree.tokens.Number(parent, content=match.group())

class Word(String):
    """
    Letters.
    """
    RE = re.compile(r'([A-Za-z]+)')
    def createToken(self, match, parent):
        return tree.tokens.Word(parent, content=match.group())

class Paragraph(MarkdownComponent):
    """
    Paragraphs (defined by regions with more than one new line)
    """
    RE = re.compile(r'\s*(?P<inline>.*?)(?:\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        return tree.tokens.Paragraph(parent)

class Backtick(MarkdownComponent):
    """
    Inline code
    """
    RE = re.compile(r"`(?P<code>[^`].+?)`", flags=re.MULTILINE|re.DOTALL)
    def createToken(self, match, parent):
        return tree.tokens.InlineCode(parent, code=match.group('code'))


class List(MarkdownComponent):
    """
    Base for lists components.
    """
    RE = None
    SPLIT_RE = None
    TOKEN = None

    def createToken(self, match, parent):
        marker = match.group('marker')
        n = len(marker)
        marker = marker.strip()

        token = self.TOKEN(parent)

        items = self.SPLIT_RE.split(match.group('items'))

        regex = re.compile(r'^ {%s}(.*?)$' % n, flags=re.MULTILINE)
        for item in items:
            root = tree.tokens.ListItem(token)
            item = regex.sub(r'\1', item)
            self.reader.parse(item, root=root)

        return token

class UnorderedList(List):
    """
    Unordered lists.
    """
    RE = re.compile(r'\s*(?P<marker>- )(?P<items>.*?)(?=\n{3,}|^[^- \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'^- ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tree.tokens.UnorderedList

class OrderedList(List):
    """
    Ordered lists.
    """
    RE = re.compile(r'\s*(?P<marker>[0-9]+\. )(?P<items>.*?)(?=\n{3,}|^[^0-9 \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'^[0-9]+\. ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tree.tokens.OrderedList

    def createToken(self, match, parent):
        token = List.createToken(self, match, parent)
        token.start = int(match.group('marker').strip('. '))
        return token

class Format(MarkdownComponent):
    """
    Inline text settings (e.g., underline, emphasis).
    """
    RE = re.compile(r'_{(?P<subscript>.*)}|'
                    r'\^{(?P<superscript>.*)}|'
                    r'\=(?P<underline>\S.*?\S)\=|'
                    r'\*(?P<emphasis>\S.*?\S)\*|'
                    r'\+(?P<strong>\S.*?\S)\+|'
                    r'~(?P<strikethrough>\S.*?\S)~',
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        for key, content in match.groupdict().iteritems():
            if content is not None:
                token = eval('tree.tokens.{}(parent, **self.attributes)'.format(key.title()))
                grammer = self.reader.lexer.grammer('inline')
                self.reader.lexer.tokenize(content, token, grammer)#, line=self.line)
                return token

class Quote(MarkdownComponent):
    """
    Block quote.
    """
    RE = re.compile(r'> (?P<block>.*?)(?=>|\n{3}|\Z)', flags=re.MULTILINE|re.DOTALL)
    def createToken(self, match, parent):
        return tree.tokens.Quote(parent)

#####################################################################################################
# Rendering.
#####################################################################################################

class CoreRenderExtension(base.RenderExtension):
    """
    HTML, Materialize, and LaTeX rendering.
    """
    def extend(self):

        self.add(tree.tokens.Heading, RenderHeading())
        self.add(tree.tokens.Code, RenderCode())
        self.add(tree.tokens.ShortcutLink, RenderShortcutLink())
        self.add(tree.tokens.InlineCode, RenderBacktick())
        self.add(tree.tokens.Break, RenderBreak())

        self.add(tree.tokens.Link, RenderLink())
        self.add(tree.tokens.Paragraph, RenderParagraph())
        self.add(tree.tokens.UnorderedList, RenderList('ul'))
        self.add(tree.tokens.OrderedList, RenderList('ol'))
        self.add(tree.tokens.ListItem, RenderListItem())
        self.add(tree.tokens.Quote, RenderTag(tag='blockquote', env='quote')
        self.add(tree.tokens.Strong, RenderTag(tag='strong', cmd='textbf')
        self.add(tree.tokens.Underline, RenderTag(tag='u', cmd='underline')
        self.add(tree.tokens.Emphasis, RenderTag(tag='em', cmd='em')
        self.add(tree.tokens.Strikethrough, RenderTag(tag='strike', cmd='sout')
        self.add(tree.tokens.Superscript, RenderSuperscript('sup'))
        self.add(tree.tokens.Subscript, RenderSubscipt('sub'))

        for t in [tree.tokens.Word, tree.tokens.Space, tree.tokens.Punctuation, tree.tokens.Number]:
            self.add(t, RenderString())

class CoreRenderComponentBase(base.RenderComponent):
    """
    Base class that includes the necessary callbacks for rendering html, materialize, and LaTeX.
    """

    def createHTML(self, token, parent):
        #TODO: Better error message with markdown line number.
        raise NotImplementedError("Not implement, you probably should.")

    def createMaterialize(self, token, parent):
        return self.createHTML(token, parent)

    def createLatex(self, token, parent):
        #TODO: Better error message with markdown line number.
        raise NotImplementedError("Not implement, you probably should.")


class RenderTag(CoreRenderComponentBase):
    """
    Basic class for creating html Tag.
    """
    TAG = None
    ENVIRONMENT = None
    COMMAND = None


    def __init__(self, tag=None, env=None, cmd=None):
        CoreRenderComponentBase.__init__(self)
        self.__tag = tag if tag is not None else self.TAG
        self.__environment = env if env is not None else self.ENVIRONMENT
        self.__command = cmd if cmd is not None else self.COMMAND

    def createHTML(self, token, parent):
        if self.__tag is None:
            raise IOError("You must have a tag.")

        return tree.html.Tag(self.__tag, parent, **token.attributes)

    def createLatex(self, token, parent):
        if self.__command is None and self.__environment is None:
            raise IOError("You must set environment or command.")

        if self.__command and self.__environment:
            raise IOError("You can't set both.")

        if self.__command:
            return tree.latex.Command(parent, command=self.__command)
        elif self.__environment:
            return tree.latex.Environment(parent, command=self.__command)

class RenderParagraph(RenderTag):
    TAG = 'p'

    def createLatex(self, token, parent):
        tree.latex.Paragraph(parent, arguments=[])
        return parent

class RenderList(RenderTag):
    def createMaterialize(self, token, parent):
        tag = RenderTag.createMaterialize(self, token, parent)
        tag['class'] = 'browser-default'
        return tag

    def createLatex(self, token, parent):
        if isinstance(token, tree.tokens.OrderedList):
            command = 'enumerate'
        else:
            command = 'itemize'
        return tree.latex.Environment(parent, command=command)

class RenderListItem(RenderTag):
    TAG = 'li'

    def createLatex(self, token, parent):
        item = tree.latex.ListItem(parent)
        return parent

class RenderSuperscript(RenderTag):



class RenderString(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        return tree.html.String(parent, content=token.content)

    def createLatex(self, token, parent):
        return tree.latex.String(parent, content=token.content)

class RenderLink(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        return tree.html.Tag('a', parent, href=token.url, **token.attributes)

    def createLatex(self, token, parent):
        return tree.latex.Href(parent, command='href', url=token.url)


class RenderBreak(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        return tree.html.String(parent, content=' ')

    def createLatex(self, token, parent):
        return tree.latex.String(parent, content=' ')

class RenderHeading(CoreRenderComponentBase):

    LATEX_COMMANDS = ['part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']
    def createHTML(self, token, parent):
        return tree.html.Tag('h{}'.format(token.level), parent, **token.attributes)

    def createLatex(self, token, parent):
        return tree.latex.Section(parent, command=self.LATEX_COMMANDS[token.level])

class RenderCode(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        language = 'language-{}'.format(token.language)
        pre = tree.html.Tag('pre', parent, **token.attributes)
        code = tree.html.Tag('code', pre, class_=language)
        string = tree.html.String(code, content=token.code)
        return pre

    def createLatex(self, token, parent):
        return tree.latex.Environment(parent, command='verbatim')

class RenderShortcutLink(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        a = tree.html.Tag('a', parent, **token.attributes)
        s = tree.html.String(a, content=token.key)

        if token.key not in SHORTCUT_DATABASE:
            msg = "The shortcut link key '%s' was not located in the list of shortcuts on line %d"
            LOG.error(msg, token.key, token.line)
        else:
            a['href'] = SHORTCUT_DATABASE[token.key]

        return a

    def createLatex(self, token, parent):

        if token.key not in SHORTCUT_DATABASE:
            msg = "The shortcut link key '%s' was not located in the list of shortcuts on line %d"
            LOG.error(msg, token.key, token.line)
        else:
            href = tree.latex.Href(parent, command='href', url=SHORTCUT_DATABASE[token.key])
            tree.latex.String(href, content=token.key)
            return href

        #return tree.latex.Command

class RenderBacktick(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        code = tree.html.Tag('code', parent)
        tree.html.String(code, content=token.code, escape=True)
        return code

    def createLatex(self, token, parent):
        code = tree.latex.Command(parent, command='texttt')
        tree.latex.String(code, content=token.code)
        return
