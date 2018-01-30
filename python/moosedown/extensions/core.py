"""
Defines the "core" extension for translating MooseDocs markdown to HTML and LaTeX.
"""
import re
import uuid
import logging
import copy

import anytree

import moosedown
from moosedown import base
from moosedown import common
from moosedown.common import exceptions
from moosedown.tree import tokens, html, latex

LOG = logging.getLogger(__name__)

def make_extension(**kwargs):
    """
    Create and return the CoreExtension object for converting from markdown to
    html/latex.
    """
    return CoreExtension(**kwargs)

class CoreExtension(base.Extension):
    """
    The core markdown extension object. Extension objects add the tokenize
    and rendering components.
    """

    def extend(self, reader, renderer):
        """
        Add the extension components.
        """
        # Block tokenize components
        reader.addBlock(Code())
        reader.addBlock(Quote())
        reader.addBlock(HeadingHash())
        reader.addBlock(OrderedList())
        reader.addBlock(UnorderedList())
        reader.addBlock(Shortcut())
        reader.addBlock(Paragraph())

        # Inline tokenize components
        reader.addInline(Monospace())
        reader.addInline(Format())
        reader.addInline(Link())
        reader.addInline(ShortcutLink())
        reader.addInline(Punctuation())
        reader.addInline(Number())
        reader.addInline(Word())
        reader.addInline(Break())
        reader.addInline(Space())

        # Render components
        renderer.add(tokens.Heading, RenderHeading())
        renderer.add(tokens.Code, RenderCode())
        renderer.add(tokens.ShortcutLink, RenderShortcutLink())
        renderer.add(tokens.Monospace, RenderMonospace())
        renderer.add(tokens.Break, RenderBreak())
        renderer.add(tokens.Exception, RenderException())

        renderer.add(tokens.Link, RenderLink())
        renderer.add(tokens.Paragraph, RenderParagraph())
        renderer.add(tokens.UnorderedList, RenderUnorderedList())
        renderer.add(tokens.OrderedList, RenderOrderedList())
        renderer.add(tokens.ListItem, RenderListItem())
        renderer.add(tokens.Quote, RenderQuote())
        renderer.add(tokens.Strong, RenderStrong())
        renderer.add(tokens.Underline, RenderUnderline())
        renderer.add(tokens.Emphasis, RenderEmphasis())
        renderer.add(tokens.Strikethrough, RenderStrikethrough())
        renderer.add(tokens.Superscript, RenderSuperscript())
        renderer.add(tokens.Subscript, RenderSubscript())
        renderer.add(tokens.Label, RenderLabel())
        renderer.add(tokens.Punctuation, RenderPunctuation())

        for t in [tokens.Word, tokens.Space, tokens.Number, tokens.String]:
            renderer.add(t, RenderString())

        #TODO: Make a generic preamble method?
        if isinstance(renderer, base.LatexRenderer):
            renderer.addPackage(u'hyperref')
            renderer.addPackage(u'ulem')


class MarkdownComponent(base.TokenComponent): #TODO: Just put this in TokenComponent
    pass

class Code(MarkdownComponent): #TODO: Rename these classes to use the word compoment so they don't get mixed with tokens names
    """
    Fenced code blocks.
    """
    RE = re.compile(r'(?:\A|\n{2,})^`{3}(?P<settings>.*?)$(?P<code>.*?)^`{3}(?=\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL)

    @staticmethod
    def defaultSettings():
        settings = MarkdownComponent.defaultSettings()
        settings['language'] = (u'text', "The code language to use for highlighting.")
        settings['caption'] = (None, "The caption text for the code listing.")
        settings['label'] = ('Listing', "The numbered caption prefix.")
        return settings

    def createToken(self, match, parent):
        if self.settings['caption']:
            flt = tokens.Float(parent, label=settings['label'], caption=settings['caption'], **self.attributes)
            return tokens.Code(flt, code=match['code'], language=self.settings['language'])
        else:
                           return tokens.Code(parent, code=match['code'],
                               language=self.settings['language'], **self.attributes)

class Quote(MarkdownComponent):
    """
    Block quote.
    """

    #TODO: settings ???
    RE = re.compile(r'(?:\A|\n{2,})(?P<quote>^>[ $].*?)(?=\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
    def createToken(self, match, parent):

        content = []
        for line in match['quote'].rstrip('\n').split('\n'):
            if line == u'>':
                content.append('')
            elif line.startswith(u'> '):
                content.append(line[2:])
            else:
                raise Exception(repr(line))

        #TODO: error check that all lines begin with '> '
        quote = tokens.Quote(parent)
        #content = self.SUB_RE.sub(r'', match['quote'])
        self.reader.parse(quote, '\n'.join(content))
        return quote

class HeadingHash(MarkdownComponent):
    """
    Hash style markdown headings with settings.

    # Heading Level One with=settings
    """
    TOKEN = tokens.Heading
    RE = re.compile(r'(?:\A|\n{2,})^(?P<level>#{1,6}) '   # match 1 to 6 #'s at the beginning of line
                    r'(?P<inline>.*?) *'                  # heading text that will be inline parsed
                    r'(?P<settings>\s+\w+=.*?)?'          # optional match key, value settings
                    r'(?=\Z|\n{2,})',                     # match up to end of string or newline(s)
                    flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    @staticmethod
    def defaultSettings():
        settings = MarkdownComponent.defaultSettings()
        return settings

    def createToken(self, match, parent):
        content = unicode(match['inline']) #TODO: is there a better way?
        heading = tokens.Heading(parent, level=match['level'].count('#'), **self.attributes)
        label = tokens.Label(heading, text=content)
        return heading

class List(MarkdownComponent):
   """
   Base for lists components.
   """
   RE = None
   ITEM_RE = None
   TOKEN = None

   def createToken(self, match, parent):

        #print 'LIST:', repr(match[0])

        marker = match['marker']
        n = len(marker)
        token = self.TOKEN(parent)
        strip_regex = re.compile(r'^ {%s}(.*?)$' % n, flags=re.MULTILINE)

        for item in self.ITEM_RE.finditer(match['items']):
            #print 'ITEM:', repr(item)
            content = ' '*n + item.group('item')
            indent = re.search(r'^\S', content, flags=re.MULTILINE|re.UNICODE)
            if indent:
                msg = "List item content must be indented by {} to match the list item " \
                      "characters of '{}', to end a list item you must use two empty lines."
                raise Exception(msg.format(n, marker))

            content = strip_regex.sub(r'\1', content)
            self.reader.parse(tokens.ListItem(token), content)

        return token

class UnorderedList(List):
   """
   Unordered lists.
   """
   RE = re.compile(r'(?:\A|\n{2,})(?P<items>(?P<marker>^- ).*?)(?=\n{3,}|\Z|\n{2}^[^-\s])',
                   flags=re.MULTILINE|re.DOTALL|re.UNICODE)
   #SPLIT = r'^- '
   #SPLIT_RE = re.compile(r'^- ', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
   ITEM_RE = re.compile(r'^- (?P<item>.*?)(?=\Z|^- )', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
   TOKEN = tokens.UnorderedList

class OrderedList(List):
   """
   Ordered lists.
   """
   RE = re.compile(r'(?:\A|\n{2,})^(?P<items>(?P<marker>[0-9]+\. ).*?)(?=\n{3,}|\Z|\n{2}^[^[0-9\s])',
                   flags=re.MULTILINE|re.DOTALL|re.UNICODE)
   ITEM_RE = re.compile(r'^[0-9]+\. (?P<item>.*?)(?=\Z|^[0-9]+\. )', flags=re.MULTILINE|re.DOTALL|re.UNICODE)

   #SPLIT_RE = re.compile(r'\n*^[0-9]+\. ', flags=re.MULTILINE|re.DOTALL)
   TOKEN = tokens.OrderedList

   #TODO: figure out how to handle settings???
   # 1. start=42 type=a This is the actual content.


   @staticmethod
   def defaultSettings():
       settings = List.defaultSettings()
       settings['type'] = ('1', "The list type (1, A, a, i, or I).")
       return settings

   def createToken(self, match, parent):
       token = List.createToken(self, match, parent)
       token.start = int(match['marker'].strip('. '))
       return token

class Shortcut(MarkdownComponent):
    """
    Markdown shortcuts.

    [foo]: something or another
    """
    RE = re.compile(r'(?:\A|\n{2,})^\[(?P<key>.*?)\]: '  # shortcut key
                    r'(?P<link>.*?)'        # shortcut value
                    r'(?=\Z|\n{2,})',             # stop new line or end of file
                    flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    def createToken(self, match, parent):
        return tokens.Shortcut(parent, key=match['key'], link=match['link'])

class Paragraph(MarkdownComponent):
    """
    Paragraphs (defined by regions with more than one new line)
    """
    RE = re.compile(r'(?:\A|\n{2,})(?P<inline>.*?)(?=\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    #TODO: Figure out settings???
    # foo=bar This is the actual content???

    def createToken(self, match, parent):
        return tokens.Paragraph(parent)

class Link(MarkdownComponent):
    """
    Markdown links [foo](bar with=settings)
    """
    RE = re.compile(r'\[(?P<inline>.*?)\]'         # link text
                    r'\((?P<url>.*?)'              # link url
                    r'(?:\s+(?P<settings>.*?))?\)' # settings
                    )

    def createToken(self, match, parent):
        return tokens.Link(parent, url=match['url'], **self.attributes)

class ShortcutLink(MarkdownComponent):
    """
    Markdown shortcut use.
    """
    RE = re.compile(r'\[(?P<key>.*?)\]', flags=re.UNICODE)
    def createToken(self, match, parent):
        return tokens.ShortcutLink(parent, key=match['key'])

class String(MarkdownComponent):
    """
    Base token for strings (i.e., words, numbers, etc.)
    """
    def createToken(self, match, parent):
        return token.String(parent, content=match[0])

class Break(String):
    """
    Line breaks.
    """
    RE = re.compile(r'(?P<break>\n+)')
    def createToken(self, match, parent):
        return tokens.Break(parent, count=len(match['break']))

class Space(String):
    """
    Spaces.
    """
    RE = re.compile(r'(?P<space> +)')
    def createToken(self, match, parent):
        return tokens.Space(parent, count=len(match['space']))

class Punctuation(String):
    """
    Not letters, numbers, or spaces.
    """
    RE = re.compile(r'([^A-Za-z0-9\s]+)')
    def createToken(self, match, parent):
        return tokens.Punctuation(parent, content=match[0])

class Number(String):
    """
    Numbers.
    """
    RE = re.compile(r'([0-9]+)')
    def createToken(self, match, parent):
        return tokens.Number(parent, content=match[0])

class Word(String):
    """
    Letters.
    """
    RE = re.compile(r'([A-Za-z]+)')
    def createToken(self, match, parent):
        return tokens.Word(parent, content=match[0])


class Monospace(MarkdownComponent):
    """
    Inline code
    """
    RE = re.compile(r"`(?P<code>.+?)`", flags=re.MULTILINE|re.DOTALL|re.DOTALL)
    def createToken(self, match, parent):
        return tokens.Monospace(parent, code=match['code'])


class Format(MarkdownComponent):
    """
    Inline text settings (e.g., monospaced, underline, emphasis).
    """
    RE = re.compile(r'\_(?P<subscript>\S.*\S)\_|'
                    r'\^(?P<superscript>\S.*\S)\^|'
                    r'\=(?P<underline>\S.*?\S)\=|'
                    r'\*(?P<emphasis>\S.*?\S)\*|'
                    r'\+(?P<strong>\S.*?\S)\+|'
                    r'~(?P<strikethrough>\S.*?\S)~',
                    flags=re.MULTILINE|re.DOTALL|re.DOTALL)

    def createToken(self, match, parent):
        for key, content in match.iteritems():
            if content is not None:
                token = eval('tokens.{}(parent, **self.attributes)'.format(key.title()))
                grammer = self.reader.lexer.grammer('inline')
                self.reader.lexer.tokenize(token, grammer, content, match.line)
                return token


#####################################################################################################
# Rendering.
#####################################################################################################


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
        pass
        #raise NotImplementedError("Not implement, you probably should.")

class RenderHeading(CoreRenderComponentBase):
    """
    Render heading.
    """
    LATEX_SECTIONS = ['part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']

    def createHTML(self, token, parent):
        #section = html.Tag(parent, 'section')
        return html.Tag(parent, 'h{}'.format(token.level), **token.attributes)

    def createLatex(self, token, parent):
        return latex.Command(parent, self.LATEX_SECTIONS[token.level], start='\n', end='\n')

class RenderLabel(CoreRenderComponentBase):
    """Label"""
    def createHTML(self, token, parent):
        pass

    def createLatex(self, token, parent):
        label = token.get('id', re.sub(r' +', r'-', token.text.lower()))
        return latex.Command(parent, 'label', string=label)

class RenderCode(CoreRenderComponentBase):
    """Code"""

    def createHTML(self, token, parent):
        language = 'language-{}'.format(token.language)
        pre = html.Tag(parent, 'pre', **token.attributes)
        code = html.Tag(pre, 'code', class_=language)
        string = html.String(code, content=token.code, escape=token.escape)
        return pre

    def createLatex(self, token, parent):
        return latex.Environment(parent, 'verbatim')

class RenderShortcutLink(CoreRenderComponentBase):
    """ShortcutLink"""

    def __init__(self, *args, **kwargs):
        CoreRenderComponentBase.__init__(self, *args, **kwargs)
        self.__cache = dict()

    def createHTML(self, token, parent):
        a = html.Tag(parent, 'a', **token.attributes)

        node = self.getShortcut(token)
        if node.content:
            html.String(a, content=node.content)
        elif node.token:
            for n in node.token.children:
                self.translator.renderer.process(n, a)
        else:
            html.String(a, content=node.key)

        a['href'] = node.link
        return a

    def createLatex(self, token, parent):
        cmd = latex.CustomCommand(parent, 'href')
        arg0 = latex.Brace(cmd, string=unicode(self.getShortcut(token)))
        arg1 = latex.Brace(cmd, string=unicode(token.key))
        return arg1

    def getShortcut(self, token):
        if token.key in self.__cache:
           # print 'CACHE:', token.key
            return self.__cache[token.key]

        for node in anytree.PreOrderIter(token.root, maxlevel=None):
           # if isinstance(node, tokens.Shortcut):
            #    print repr(node)
            if isinstance(node, tokens.Shortcut) and node.key == token.key:
                self.__cache[token.key] = node
                return node

        msg = "The shortcut link key '{}' was not located in the list of shortcuts."
        raise KeyError(msg.format(token.key))


class RenderMonospace(CoreRenderComponentBase):
    """InlineCode"""

    def createHTML(self, token, parent):
        code = html.Tag(parent, 'code')
        html.String(code, content=token.code, escape=True)
        return code

    def createLatex(self, token, parent):
        code = latex.Command(parent, 'texttt')
        latex.String(code, content=token.code)
        return

class RenderBreak(CoreRenderComponentBase):
    """Break"""

    def createHTML(self, token, parent):
        return html.String(parent, content=u' ')

    def createLatex(self, token, parent):
        return latex.String(parent, content=u' ')

class RenderLink(CoreRenderComponentBase):
    """Link"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'a', href=token.url, **token.attributes)

    def createLatex(self, token, parent):
        url = token.url.lstrip('#')
        cmd = latex.CustomCommand(parent, 'href')
        arg0 = latex.Brace(cmd, string=url)
        arg1 = latex.Brace(cmd)
        return arg1

class RenderParagraph(CoreRenderComponentBase):
    """Paragraph"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'p', **token.attributes)

    def createLatex(self, token, parent):
        latex.CustomCommand(parent, 'par', start='\n', end='\n')
        return parent

class RenderOrderedList(CoreRenderComponentBase):
    """OrderedList"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'ol', **token.attributes)

    def createMaterialize(self, token, parent):
        tag = CoreRenderComponentBase.createMaterialize(self, token, parent)
        tag['class'] = 'browser-default'
        tag['start'] = token.start
        #tag['type'] = token.type
        return tag

    def createLatex(self, token, parent):
        return latex.Environment(parent, 'enumerate')

class RenderUnorderedList(CoreRenderComponentBase):
    """UnorderedList"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'ul', **token.attributes)

    def createMaterialize(self, token, parent):
        tag = CoreRenderComponentBase.createMaterialize(self, token, parent)
        tag['class'] = 'browser-default'
        return tag

    def createLatex(self, token, parent):
        return latex.Environment(parent, 'itemize')

class RenderListItem(CoreRenderComponentBase):
    """ListItem"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'li', **token.attributes)

    def createLatex(self, token, parent):
        item = latex.CustomCommand(parent, 'item', start='\n')
        return parent

class RenderString(CoreRenderComponentBase):
    """String"""

    def createHTML(self, token, parent):
        #if parent.name =='td':
        #    print parent
        return html.String(parent, content=token.content)

    def createLatex(self, token, parent):
        return latex.String(parent, content=token.content)

class RenderQuote(CoreRenderComponentBase):
    """Blockquote"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'blockquote', **token.attributes)

    def createLatex(self, token, parent):
        return latex.Environment(parent, 'quote')

class RenderStrong(CoreRenderComponentBase):
    """Strong"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'strong', **token.attributes)

    def createLatex(self, token, parent):
        return latex.Command(parent, 'textbf')

class RenderUnderline(CoreRenderComponentBase):
    """Underline"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'u', **token.attributes)

    def createLatex(self, token, parent):
        return latex.Command(parent, 'underline')

class RenderEmphasis(CoreRenderComponentBase):
    """Emphasis"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'em', **token.attributes)

    def createLatex(self, token, parent):
        return latex.Command(parent, 'emph')

class RenderStrikethrough(CoreRenderComponentBase):
    """Strikethrough"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'strike', **token.attributes)

    def createLatex(self, token, parent):
        return latex.Command(parent, 'sout')

class RenderSuperscript(CoreRenderComponentBase):
    """Superscript"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'sup', **token.attributes)

    def createLatex(self, token, parent):
        math = latex.InlineMath(parent)
        latex.String(math, content=u'^{')
        cmd = latex.Command(math, 'text')
        latex.String(math, content=u'}')
        return cmd

class RenderSubscript(CoreRenderComponentBase):
    """Subscript"""

    def createHTML(self, token, parent):
        return html.Tag(parent, 'sub', **token.attributes)

    def createLatex(self, token, parent):
        math = latex.InlineMath(parent)
        latex.String(math, content=u'_{')
        cmd = latex.Command(math, 'text')
        latex.String(math, content=u'}')
        return cmd

class RenderPunctuation(RenderString):
    def createHTML(self, token, parent):
        if token.content == u'--':
            return html.String(parent, content=u'&ndash;')
        elif token.content == u'---':
            return html.String(parent, content=u'&mdash;')

        return RenderString.createHTML(self, token, parent)

class RenderException(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        div = html.Tag(parent, 'div', class_="moose-exception", **token.attributes)
        html.String(div, content=token.info[0])
        return div

    def createMaterialize(self, token, parent):
        id_ = uuid.uuid4()
        a = html.Tag(parent, 'a', class_="moose-exception modal-trigger", href='#{}'.format(id_))
        html.String(a, content=token.info[0])

        modal = html.Tag(parent.root, 'div', id_=id_, class_="modal")
        content = html.Tag(modal, 'div', class_="modal-content")
        head = html.Tag(content, 'h2')
        html.String(head, content=u'Tokenize Exception')
        p = html.Tag(content, 'p')

        msg = u"An exception occurred while tokenizing, the exception was " \
              u"raised when executing the {} object while processing the " \
              u"following content.".format(token.info.pattern.name)
        html.String(p, content=msg)
        html.Tag(p, 'br', close=False)

        #fname = html.Tag(p, 'a', target="_blank", href=r"file://{}".format(token.root.page.source))
        #html.String(fname, content=u"{}:{}".format(token.root.page.source, token.info.line))

        pre = html.Tag(content, 'pre')
        code = html.Tag(pre, 'code', class_="language-markdown")
        html.String(code, content=token.info[0], escape=True)

        pre = html.Tag(content, 'pre', style="font-size:80%;")
        html.String(pre, content=unicode(token.traceback), escape=True)
        #print token.traceback

        footer = html.Tag(modal, 'div', class_="modal-footer grey lighten-3")
        done = html.Tag(footer, 'a', class_="modal-action modal-close btn-flat")
        html.String(done, content=u"Done")

        return content
