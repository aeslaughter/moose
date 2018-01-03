"""
This defines the core Markdown translation to HTML and LaTeX.
"""
import re
import uuid
import logging

import moosedown
from moosedown import base
from moosedown import common
from moosedown.tree import tokens, html, latex

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
        config['section-level'] = (2, "The section level for creating collapsible sections and scrollspy.")
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



class Code(MarkdownComponent):
    """
    Fenced code blocks.
    """
    RE = re.compile(r'\s*`{3}(?P<settings>.*?)$(?P<code>.*?)`{3}', flags=re.MULTILINE|re.DOTALL)

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
            return tokens.Code(flt, code=match.group('code'), language=self.settings['language'])
        else:
            return tokens.Code(parent, code=match.group('code'),
                               language=self.settings['language'], **self.attributes)

class HeadingHash(MarkdownComponent):
    """
    Hash style markdown headings with settings.

    # Heading Level One with=settings
    """
    TOKEN = tokens.Heading
    RE = re.compile(r'\s*(?P<level>#{1,6})\s'    # match 1 to 6 #'s at the beginning of line
                    r'(?P<inline>.*?)'           # heading text that will be inline parsed
                    r'(?P<settings>\s+\w+=.*?)?' # optional match key, value settings
                    r'(?:\Z|\n+)',               # match up to end of string or newline(s)
                    flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    @staticmethod
    def defaultSettings():
        settings = MarkdownComponent.defaultSettings()
        #settings['collapsible'] = (True, "Enable/disable the collapsible feature when using MaterializeRenderer.")
        return settings

    def createToken(self, match, parent):
        content = unicode(match.group('inline')) #TODO: is there a better way?
        heading = tokens.Heading(parent, level=match.group('level').count('#'), **self.attributes)
        label = tokens.Label(heading, text=content)
        return heading

class Link(MarkdownComponent):
    """
    Markdown links [foo](bar with=settings)
    """
    RE = re.compile(r'\[(?P<inline>.*?)\]'         # link text
                    r'\((?P<url>.*?)'              # link url
                    r'(?:\s+(?P<settings>.*?))?\)' # settings
                    )

    def createToken(self, match, parent):
        return tokens.Link(parent, url=match.group('url'), **self.attributes)

class Shortcut(MarkdownComponent):
    """
    Markdown shortcuts.

    [foo]: something or another
    """
    RE = re.compile(r'\s*\[(?P<key>.*?)\]:\s'  # shortcut key
                    r'(?P<content>.*?)'        # shortcut value
                    r'(?:\n+|\Z)',             # stop new line or end of file
                    flags=re.MULTILINE|re.UNICODE)

    def createToken(self, match, parent):
        token = tokens.Shortcut(parent, key=match.group('key'), content=match.group('content'))

        #TODO: remove this database, just look at the tree when rendering
        SHORTCUT_DATABASE[token.key] = token.content
        return token

class ShortcutLink(MarkdownComponent):
    """
    Markdown shortcut use.
    """
    RE = re.compile(r'\[(?P<key>.*?)\]')
    def createToken(self, match, parent):
        return tokens.ShortcutLink(parent, key=match.group('key'))

class String(MarkdownComponent):
    """
    Base token for strings (i.e., words, numbers, etc.)
    """
    def createToken(self, match, parent):
        return token.String(parent, content=match.group())

class Break(String):
    """
    Line breaks.
    """
    RE = re.compile(r'(?P<break>\n+)')
    def createToken(self, match, parent):
        return tokens.Break(parent, count=len(match.group('break')))

class Space(String):
    """
    Spaces.
    """
    RE = re.compile(r'(?P<space> +)')
    def createToken(self, match, parent):
        return tokens.Space(parent, count=len(match.group('space')))

class Punctuation(String):
    """
    Not letters, numbers, or spaces.
    """
    RE = re.compile(r'([^A-Za-z0-9\s]+)')
    def createToken(self, match, parent):
        return tokens.Punctuation(parent, content=match.group())

class Number(String):
    """
    Numbers.
    """
    RE = re.compile(r'([0-9]+)')
    def createToken(self, match, parent):
        return tokens.Number(parent, content=match.group())

class Word(String):
    """
    Letters.
    """
    RE = re.compile(r'([A-Za-z]+)')
    def createToken(self, match, parent):
        return tokens.Word(parent, content=match.group())

class Paragraph(MarkdownComponent):
    """
    Paragraphs (defined by regions with more than one new line)
    """
    RE = re.compile(r'\s*(?P<inline>.*?)(?:\Z|\n{2,})', flags=re.MULTILINE|re.DOTALL|re.UNICODE)

    #TODO: Figure out settings???
    # foo=bar This is the actual content???

    def createToken(self, match, parent):
        return tokens.Paragraph(parent)

class Backtick(MarkdownComponent):
    """
    Inline code
    """
    RE = re.compile(r"`(?P<code>[^`].+?)`", flags=re.MULTILINE|re.DOTALL)
    def createToken(self, match, parent):
        return tokens.InlineCode(parent, code=match.group('code'))



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
            if not item:
                continue
            root = tokens.ListItem(token)
            item = regex.sub(r'\1', item)
            self.reader.parse(item, root=root)

        return token

class UnorderedList(List):
    """
    Unordered lists.
    """
    RE = re.compile(r'\s*^(?P<items>(?P<marker>-\s).*?)(?=\n{3,}|^[^- \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'\n*^- ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tokens.UnorderedList

class OrderedList(List):
    """
    Ordered lists.
    """
    RE = re.compile(r'\s*(?P<marker>[0-9]+\. )(?P<items>.*?)(?=\n{3,}|^[^0-9 \n]|\Z)',
                    flags=re.MULTILINE|re.DOTALL)
    SPLIT_RE = re.compile(r'\n*^[0-9]+\. ', flags=re.MULTILINE|re.DOTALL)
    TOKEN = tokens.OrderedList

    #TODO: figure out how to handle settings???
    # 1. start=42 type=a This is the actual content.


    @staticmethod
    def defaultSettings():
        settings = List.defaultSettings()
        settings['type'] = ('1', "The list type (1, A, a, i, or I).")

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
                token = eval('tokens.{}(parent, **self.attributes)'.format(key.title()))
                grammer = self.reader.lexer.grammer('inline')
                self.reader.lexer.tokenize(content, token, grammer)#, line=self.line)
                return token

class Quote(MarkdownComponent):
    """
    Block quote.
    """
    SUB_RE = re.compile(r'^> {0,1}', flags=re.MULTILINE)
    RE = re.compile(r'\s*(?P<quote>^>[ $].*?)(?=^[^>]|\Z)', flags=re.MULTILINE|re.DOTALL|re.UNICODE)
    def createToken(self, match, parent):
        quote = tokens.Quote(parent)
        content = self.SUB_RE.sub(r'', match.group('quote'))
        self.reader.parse(content, root=quote)
        return quote

#####################################################################################################
# Rendering.
#####################################################################################################

class CoreRenderExtension(base.RenderExtension):
    """
    HTML, Materialize, and LaTeX rendering.
    """
    def extend(self):

        self.add(tokens.Heading, RenderHeading())
        self.add(tokens.Code, RenderCode())
        self.add(tokens.ShortcutLink, RenderShortcutLink())
        self.add(tokens.InlineCode, RenderBacktick())
        self.add(tokens.Break, RenderBreak())
        self.add(tokens.Exception, RenderException())

        self.add(tokens.Link, RenderLink())
        self.add(tokens.Paragraph, RenderParagraph())
        self.add(tokens.UnorderedList, RenderUnorderedList())
        self.add(tokens.OrderedList, RenderOrderedList())
        self.add(tokens.ListItem, RenderListItem())
        self.add(tokens.Quote, RenderQuote())
        self.add(tokens.Strong, RenderStrong())
        self.add(tokens.Underline, RenderUnderline())
        self.add(tokens.Emphasis, RenderEmphasis())
        self.add(tokens.Strikethrough, RenderStrikethrough())
        self.add(tokens.Superscript, RenderSuperscript())
        self.add(tokens.Subscript, RenderSubscript())
        self.add(tokens.Label, RenderLabel())

        for t in [tokens.Word, tokens.Space, tokens.Punctuation, tokens.Number]:
            self.add(t, RenderString())

        #TODO: Make a generic preamble method?
        if isinstance(self.renderer, base.LatexRenderer):
            self.renderer.addPackage(u'hyperref')
            self.renderer.addPackage(u'ulem')

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

class RenderHeading(CoreRenderComponentBase):
    """
    Render heading.
    """
    LATEX_SECTIONS = ['part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']

    def createHTML(self, token, parent):
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

    def createHTML(self, token, parent):
        a = html.Tag(parent, 'a', **token.attributes)
        s = html.String(a, content=token.key)

        if token.key not in SHORTCUT_DATABASE:
            msg = "The shortcut link key '{}' was not located in the list of shortcuts."
            raise KeyError(msg.format(token.key))
        else:
            a['href'] = SHORTCUT_DATABASE[token.key]
        return a

    def createLatex(self, token, parent):
        if token.key not in SHORTCUT_DATABASE:
            msg = "The shortcut link key '{}' was not located in the list of shortcuts."
            raise Exception(msg.format(token.key))
        else:
            cmd = latex.CustomCommand(parent, 'href')
            arg0 = latex.Brace(cmd, string=unicode(SHORTCUT_DATABASE[token.key]))
            arg1 = latex.Brace(cmd, string=unicode(token.key))
            return arg1

class RenderBacktick(CoreRenderComponentBase):
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

class RenderException(CoreRenderComponentBase):
    def createHTML(self, token, parent):
        div = html.Tag(parent, 'div', class_="moose-exception", **token.attributes)
        html.String(div, content=token.match.group())
        return div

    def createMaterialize(self, token, parent):
        id_ = uuid.uuid4()
        a = html.Tag(parent, 'a', class_="moose-exception modal-trigger", href='#{}'.format(id_))
        html.String(a, content=token.match.group())

        modal = html.Tag(parent, 'div', id_=id_, class_="modal")
        content = html.Tag(modal, 'div', class_="modal-content")
        head = html.Tag(content, 'h2')
        html.String(head, content=u'Tokenize Exception')
        p = html.Tag(content, 'p')

        msg = u"An exception occurred while tokenizing, the exception was " \
              u"raised when executing the {} object while processing the " \
              u"following content.".format(token.pattern.name)
        html.String(p, content=msg)
        html.Tag(p, 'br', close=False)
        fname = html.Tag(p, 'a', target="_blank", href=r"file://{}".format(token.source))
        html.String(fname, content=u"{}:{}".format(token.source, token.line))

        pre = html.Tag(content, 'pre')
        code = html.Tag(pre, 'code', class_="language-markdown")
        html.String(code, content=token.match.group(0), escape=True)

        pre = html.Tag(content, 'pre', style="font-size:80%;")
        html.String(pre, content=unicode(token.traceback), escape=True)
        #print token.traceback

        footer = html.Tag(modal, 'div', class_="modal-footer grey lighten-3")
        done = html.Tag(footer, 'a', class_="modal-action modal-close btn-flat")
        html.String(done, content=u"Done")

        return content
