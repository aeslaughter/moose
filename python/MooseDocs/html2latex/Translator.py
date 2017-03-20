import re
import bs4
import cgi
import uuid
import copy
from pylatexenc.latexencode import utf8tolatex
import logging
log = logging.getLogger(__name__)
from Extension import Extension
from ElementStorage import ElementStorage
import elements

class Translator(object):
    """
    Class for converting from html to latex.

    Args:
      extensions[list]: List of Extension objects. If empty the BasicExtension will be used.
    """
    ESCAPE_MAP = dict()
    ESCAPE_MAP['_'] = '\\_'
    ESCAPE_MAP['{'] = '\\{'
    ESCAPE_MAP['}'] = '\\}'
    ESCAPE_MAP['$'] = '\\$'
    ESCAPE_MAP['&'] = '\\&'
    ESCAPE_MAP['%'] = '\\%'
    ESCAPE_MAP['\\'] = '\\textbackslash~'
    ESCAPE_MAP['~'] = '\\textasciitilde~'
    ESCAPE_MAP['^'] = '\\textasciicircum~'

    def __init__(self, extensions=[]):

        #: BlockElement objects
        self.elements = ElementStorage(etype=elements.Element)

        # Add extensions
        for e in extensions:
            if isinstance(e, type):
                obj = e()
            else:
                obj = e

            if not isinstance(obj, Extension):
                raise Exception('Invalid extension type or instance provided, expected {} but was given {}.'.format('Extension', type(e)))
            obj.extend(self)

    def convert(self, html):
        """
        Convert supplied html to latex.

        Args:
          html[str]: The raw html to convert to latex.
        """

        # The html parser attempts to match < > even when they are inside code blocks
        lt = str(uuid.uuid4())
        gt = str(uuid.uuid4())
        def subAngleBrackets(match):
            return u'<code{}>{}</code>'.format(match.group(1),
                                               match.group(2).replace('<', lt).replace('>', gt))
        html = re.sub(r'<code(.*?)>(.*?)</code>', subAngleBrackets, html, flags=re.MULTILINE|re.DOTALL)

        # Parse the HTML and convert tags for latex conversion
        soup = bs4.BeautifulSoup(html, "lxml")
        for elem in self.elements:
            for tag in soup.descendants:
                elem(soup, tag)

        # Label unknown HTML for verbatim output
        for child in soup.descendants:
            if isinstance(child, bs4.element.Tag) and (child.name != 'latex') and (len(child.contents) == 1)  and isinstance(child.contents[0], bs4.element.NavigableString):
                log.error('Failed to convert tag {}: {}'.format(child.name, str(child)))
                tex = soup.new_tag('latex')
                tex.string = unicode(child)
                tex['data-latex-begin'] = '\\begin{verbatim}'
                tex['data-latex-end'] = '\\end{verbatim}'
                tex['data-latex-begin-suffix'] = '\n'
                tex['data-latex-end-prefix'] = '\n'
                child.replace_with(tex)

        # Convert the latex
        output = ''.join(x for x in self.process(soup) if x is not None)
        return output.replace(lt, '<').replace(gt, '>')


    @staticmethod
    def process(tag):

        if isinstance(tag, elements.LatexNavigableString):
            yield utf8tolatex(tag.strip('\n'), non_ascii_only=True, brackets=False)

        elif isinstance(tag, bs4.element.NavigableString):
            yield utf8tolatex(Translator.escape(tag).strip('\n'), non_ascii_only=True, brackets=False)

        else:
            yield tag.get('data-latex-open')
            yield tag.get('data-latex-begin-prefix')
            yield tag.get('data-latex-begin')
            yield tag.get('data-latex-begin-suffix')

            for child in tag.children:
                for p in Translator.process(child):
                    yield p

            yield tag.get('data-latex-end-prefix')
            yield tag.get('data-latex-end')
            yield tag.get('data-latex-end-suffix')
            yield tag.get('data-latex-close')

    @staticmethod
    def escape(content):
        """
        Escape special latex characters.
        """
        def sub(match):
            return Translator.ESCAPE_MAP[match.group(1)]
        return re.sub(r'([_{}$\\%&~^])', sub, content)
