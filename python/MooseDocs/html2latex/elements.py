import bs4
import mooseutils

class Element(object):
    """
    Base class for converting html tag to latex.
    """
    name = None
    attrs = []

    def __init__(self):
        pass

    def test(self, tag):
        if isinstance(tag, bs4.element.Tag) and tag.name == self.name and all([a in tag.attrs for a in self.attrs]):
            return True
        return False

    @staticmethod
    def content(tag, escape=True):
        """
        Creates complete content contained within this tag and escapes _ in raw text.
        """
        return u''.join([unicode(c) for c in tag.children])

    def convert(self, tag):
        tag.insert_before(bs4.element.NavigableString(self.before(tag)))
        tag.insert_after(bs4.element.NavigableString(self.after(tag)))
        tag.unwrap()

    def before(self, tag):
        return str()

    def after(self, tag):
        return str()

class BlockElement(Element):
    command = None
    def __init__(self, *args, **kwargs):
        super(BlockElement, self).__init__(*args, **kwargs)
        if self.command is None:
            raise mooseutils.MooseException('The "command" class member must be set.')
        self.begin = '\\begin{%s}\n' % self.command
        self.end = '\n\\end{%s}' % self.command
    def before(self, tag):
        return self.begin
    def after(self, tag):
        return self.end

class InlineElement(Element):
    """
    InlineElements are 'inline', says Cpt. Obvious.
    """
    command = None
    def __init__(self, *args, **kwargs):
        super(InlineElement, self).__init__(*args, **kwargs)
        if self.command is None:
            raise mooseutils.MooseException('The "command" class member must be set.')

    def before(self, tag):
        return '\\%s{' % self.command

    def after(self, tag):
        return '}'

class InlineHeading(InlineElement):
    def __init__(self, command=None):
        if command is None:
            raise mooseutils.MooseException("The 'command' argument must be supplied.")
        self.command = command

    def after(self, tag):
        if 'id' in tag.attrs:
            return '\\label{%s}}' % tag['id']
        else:
            return '}'

class html(Element):
    name = 'html'

class body(Element):
    name = 'body'

class head(Element):
    name = 'head'

class h1(InlineHeading):
    name = 'h1'

class h2(InlineHeading):
    name = 'h2'

class h3(InlineHeading):
    name = 'h3'

class h4(InlineHeading):
    name = 'h4'

class h5(InlineHeading):
    name = 'h5'

class h6(InlineHeading):
    name = 'h6'

class div(Element):
    name = 'div'

class pre_code(BlockElement):
    name = 'pre'
    command = 'verbatim'
    def test(self, tag):
        return super(pre_code, self).test(tag) and (tag.code)
    def convert(self, tag):
        tag.code.unwrap()
        super(pre_code, self).convert(tag)

class pre(BlockElement):
    name = 'pre'
    command = 'verbatim'

class table(BlockElement):
    name = 'table'
    command ='tabular'
    def before(self, tag):
        tr = tag.tbody.find_all('tr')
        return '\\begin{tabular}{%s}\n' % ('l'*len(tr))

class tbody(Element):
    name = 'tbody'

class thead(Element):
    name = 'thead'
    def before(self, tag):
        return '\\hline\n'
    def after(self, tag):
        return '\\hline'

class tfoot(thead):
    name = 'tfoot'

class tr(Element):
    name = 'tr'
    def after(self, tag):
        print tag
        return '\n'

class th(Element):
    name = 'th'
    def after(self, tag):
        if tag.find_next_sibling(self.name):
            return ' & '
        return ' \\\\'

class td(th):
    name = 'td'

class ol(BlockElement):
    name = 'ol'
    command = 'enumerate'

class ul(BlockElement):
    name = 'ul'
    command = 'itemize'

class li(Element):
    name = 'li'
    def before(self, tag):
        return '\\item '
    def after(self, tag):
        if tag.find_next_sibling('li'):
            return '\n'
        return ''

class inline_equation(Element):
    name = 'script'
    attrs = ['type']

    def test(self, tag):
        return super(inline_equation, self).test(tag) and (tag['type'] == u'math/tex')
    def before(self, tag):
        return '$'
    def after(self, tag):
        return '$'

class equation(BlockElement):
    name = 'script'
    attrs = ['type']
    command = 'equation'

    def test(self, tag):
        tf = super(equation, self).test(tag)
        return tf and (tag['type'] == u'math/tex; mode=display')
    def before(self, tag):
        content = self.content(tag)
        if self.begin in content:
            return ''
        else:
            return super(equation, self).before(tag)

class hr(Element):
    name = 'hr'
    def before(self, tag):
        return '\\hrule\n'

class figcaption(InlineElement):
    name = 'figcaption'
    command = 'caption'

class img(InlineElement):
    name = 'img'
    attrs = ['src']
    command = 'includegraphics'
    def after(self, tag):
        return tag['src'] + '}\n'

class figure(BlockElement):
    name = 'figure'
    command = 'figure'

class a(Element):
    name = 'a'
    attrs = ['href']
    def before(self, tag):
        return '\\href{%s}{' % tag['href']
    def after(self, tag):
        return '}'

class span(Element):
    name = 'span'

class p(Element):
    name = 'p'
    def before(self, tag):
        return '\\par\n'
    def after(self, tag):
        return '\n'

class code(InlineElement):
    name = 'code'
    command = 'texttt'

class em(InlineElement):
    name = 'em'
    command = 'emph'

class unknown(BlockElement):
    command = 'verbatim'

class center(BlockElement):
    name = 'center'
    command = 'center'
