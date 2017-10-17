"""
This defines the core Markdown translation to HTML and LaTeX. The HTML conversion is compliant
with the CommonMark standard (http://spec.commonmark.org/).
"""
import re

import MooseDocs
from MooseDocs import common
from MooseDocs import tree
from Extension import MarkdownExtension, RenderExtension
from Component import TokenComponent, RenderComponent, TokenComponent

SHORTCUT_DATABASE = dict()

def make_extension():
    return CoreMarkdownExtension(), CoreRenderExtension()

class CoreMarkdownExtension(MarkdownExtension):

    @staticmethod
    def getConfig():
        config = MarkdownExtension.getConfig()
        return config

    def extend(self):

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

class MarkdownComponent(TokenComponent):
    @staticmethod
    def defaultSettings():
        settings = TokenComponent.defaultSettings()
        settings['style'] = ('', "The style settings that are passed to the HTML flags.")
        settings['class'] = ('', "The class settings to be passed to the HTML flags.")
        settings['id'] = ('', "The class settings to be passed to the HTML flags.")
        return settings

    @property
    def attributes(self):
        return dict(style=self.settings['style'], id_=self.settings['id'], class_=self.settings['class'])

class Command(MarkdownComponent):
    RE = re.compile('!(?P<command>\w+)\s(?P<subcommand>\w+)(?P<settings>.*?$)?(?P<content>.*?)\n{2,}|\Z',
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        cmd = (match.group('command'), match.group('subcommand'))

        #TODO: Error check
        if cmd not in MarkdownExtension.__COMMANDS__:
            return tree.tokens.String(parent, match.group())

        obj = MarkdownExtension.__COMMANDS__[cmd]
        obj.settings = self.settings
        obj.line = self.line
        token = obj.createToken(match, parent)
        return token

class Code(MarkdownComponent):
    RE = re.compile(r'\s*`{3}(?P<language>\w+)?(?P<settings>.*?)$(?P<code>.*?)`{3}',
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        return tree.tokens.Code(parent, code=match.group('code'), **self.attributes)


class HeadingHash(MarkdownComponent):

    TOKEN = tree.tokens.Heading
    RE = re.compile(r'\s*(?P<level>#{1,6})\s' # match 1 to 6 #'s at the beginning of line
                    r'(?P<inline>.*?)'        # heading text that will be inline parsed
                    r'(?P<settings>\w+=.*?)?' # optional match key, value settings
                    r'(?:\Z|\n+)',            # match up to end of string or newline(s)
                    flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        return tree.tokens.Heading(parent, level=match.group('level').count('#'), **self.attributes)

class Link(MarkdownComponent):
    RE = re.compile(r'\[(?P<inline>.*?)\]'         # link text
                    r'\((?P<url>.*?)'              # link url
                    r'(?:\s+(?P<settings>.*?))?\)' # settings
                    )

    def createToken(self, match, parent):
        return tree.tokens.Link(parent, href=match.group('url'), **self.attributes)


class Shortcut(MarkdownComponent):
    RE = re.compile(r'\s*\[(?P<key>.*?)\]:\s'     # shortcut key
                    r'(?P<content>.*?)'        # shortcut value
                    #r'(?P<settings>\w+=.*?)?'  # optional settings
                    r'\n+',                    # stop at non-whitespace at beginning of new line
                    flags=re.MULTILINE)

    def createToken(self, match, parent):
        token = tree.tokens.Shortcut(parent, key=match.group('key'), content=match.group('content'))
        SHORTCUT_DATABASE[token.key] = token.content
        return token

class ShortcutLink(MarkdownComponent):
    RE = re.compile(r'\[(?P<key>.*?)\]')
    def createToken(self, match, parent):
        return tree.tokens.ShortcutLink(parent, key=match.group('key'))

class String(MarkdownComponent):
    def createToken(self, match, parent):
        return token.String(parent, content=match.group())

class Break(String):
    RE = re.compile(r'(?P<break>\n+)')
    def createToken(self, match, parent):
        return tree.tokens.Break(parent, count=len(match.group('break')))

class Space(String):
    RE = re.compile(r'(?P<space> +)')
    def createToken(self, match, parent):
        return tree.tokens.Space(parent, count=len(match.group('space')))

class Punctuation(String):
    RE = re.compile(r'([^A-Z|^a-z|^0-9|^\s]+)')
    def createToken(self, match, parent):
        return tree.tokens.Punctuation(parent, content=match.group())

class Number(String):
    RE = re.compile(r'([0-9]+)')
    def createToken(self, match, parent):
        return tree.tokens.Number(parent, content=match.group())

class Word(String):
    RE = re.compile(r'([A-Za-z]+)')
    def createToken(self, match, parent):
        return tree.tokens.Word(parent, content=match.group())

class Paragraph(MarkdownComponent):
    RE = re.compile(r'\s*(?P<inline>.*?)(?:\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        return tree.tokens.Paragraph(parent)

class Backtick(MarkdownComponent):
    RE = re.compile(r"`(?P<code>[^`].+?)`", flags=re.MULTILINE|re.DOTALL)
    def createToken(self, match, parent):
        return tree.tokens.InlineCode(parent, content=match.group('code'))


class List(MarkdownComponent):
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
    RE = re.compile(r'\s*(?P<marker>- )(?P<items>.*?)(?=\n{3,}|^[^- \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'^- ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tree.tokens.UnorderedList


class OrderedList(List):
    RE = re.compile(r'\s*(?P<marker>[0-9]+\. )(?P<items>.*?)(?=\n{3,}|^[^0-9 \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'^[0-9]+\. ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tree.tokens.OrderedList

class Format(MarkdownComponent):
    RE = re.compile(r'(?P<star>\*{1,3})(?P<content>.*)', flags=re.MULTILINE|re.DOTALL)

    def createToken(self, match, parent):
        content = match.group('content')
        n = len(match.group('star'))
        token = None

        # Start
        if len(content) > 0 and content[0] != ' ':
            if n == 3:
                token = tree.tokens.Emphasis(tree.tokens.Strong(parent))
            elif n == 2:
                token = tree.tokens.Strong(parent)
            else: # n == 1
                token = tree.tokens.Emphasis(parent)

        else:
            if n == 3:
                token = parent.parent.parent
            else:
                token = parent.parent

        grammer = self.reader.lexer.grammer('inline')
        self.reader.lexer.tokenize(content, token, grammer, line=self.line)

        return token


class Quote(MarkdownComponent):
    RE = re.compile(r'> (?P<block>.*?)(?=>|\n{3}|\Z)', flags=re.MULTILINE|re.DOTALL)
    def createToken(self, match, parent):
        return tree.tokens.Quote(parent)


class CoreRenderExtension(RenderExtension):
    def extend(self):
        self.add(tree.tokens.Heading, RenderHeading())
        self.add(tree.tokens.Code, RenderCode())

        self.add(tree.tokens.ShortcutLink, RenderShortcutLink())
        self.add(tree.tokens.InlineCode, RenderBacktick())

        self.add(tree.tokens.Link, RenderTag('a'))
        self.add(tree.tokens.Paragraph, RenderTag('p'))
        self.add(tree.tokens.UnorderedList, RenderTag('ul'))
        self.add(tree.tokens.OrderedList, RenderTag('ol'))
        self.add(tree.tokens.ListItem, RenderTag('li'))
        self.add(tree.tokens.Strong, RenderTag('strong'))
        self.add(tree.tokens.Emphasis, RenderTag('em'))
        self.add(tree.tokens.Quote, RenderTag('blockquote'))

        for t in [tree.tokens.Word, tree.tokens.Space, tree.tokens.Punctuation, tree.tokens.Break,
                  tree.tokens.Number]:
            self.add(t, RenderString())

class CoreRenderComponentBase(RenderComponent):

    def createHTML(self, token, parent):
        raise NotImplementedError("Not implement, you probably should.")

    def createMaterialize(self, token, parent):
        return self.createHTML(token, parent)


class RenderTag(CoreRenderComponentBase):
    def __init__(self, tag, *args, **kwargs):
        RenderComponent.__init__(self, *args, **kwargs)
        self.__tag = tag

    def createHTML(self, token, parent):
        return tree.html.Tag(self.__tag, parent, **token.settings)

class RenderString(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        return tree.html.String(token.content, parent)

class RenderHeading(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        return tree.html.Tag('h{}'.format(token.level), parent, **token.settings)

class RenderCode(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        pre = tree.html.Tag('pre', parent, **token.settings)
        code = tree.html.Tag('code', pre)
        string = tree.html.String(token.code, code)
        return pre

class RenderShortcutLink(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        a = tree.html.Tag('a', parent, **token.settings)
        s = tree.html.String(token.key, a)

        if token.key not in SHORTCUT_DATABASE:
            token.error("The shortcut link key '{}' was not located in the list of shortcuts.".format(token.key))
        else:
            a['href'] = SHORTCUT_DATABASE[token.key]

        return a

class RenderBacktick(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        code = tree.html.Tag('code', parent)
        tree.html.String(token.content, parent=code, escape=True)
        return code
