import re
import bs4
import copy
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
    def __init__(self, unknown=elements.unknown(), extensions=[]):

        #: BlockElement objects
        self.elements = ElementStorage(etype=elements.Element)

        #: Unknown tag conversion
        self.unknown = unknown

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
        #def subAngleBrackets(match):
        #    return 'u<code{}>{}</code>'.format(match.group(1), match.group(2).replace('<', #'##LESSTHAN##').replace('>', #'##GREATERTHAN##').replace('&lt;','##LESSTHAN##').replace('&gt;','##GREATERTHAN##'))
        #html = re.sub(r'<code(.*?)>(.*?)</code>', subAngleBrackets, html,
        #flags=re.MULTILINE|re.DOTALL)

        # Replace html's unicode quotation marks with those used by latex
        #def subQuoteMarks(match):
        #    return u'<p>{}</p>'.format(match.group(1).replace('&ldquo;','``').replace('&rdquo;','\'\'').replace('&lsquo;','`').replace('&rsquo;','\''))
        #tml = re.sub(r'<p>(.*?)</p>', subQuoteMarks, html, flags=re.MULTILINE|re.DOTALL)

        def html2latex(soup):
            keep_going = False
            for elem in self.elements:
                for tag in soup.find_all(elem.name):
                    if elem.test(tag):
                        elem.convert(tag)
                        keep_going = True
                        #break
            return keep_going


        soup = bs4.BeautifulSoup(html, "lxml")

        just_go = True
        while (just_go):
            just_go = html2latex(soup)

        for child in soup.descendants:
            if isinstance(child, bs4.element.Tag):
                log.error('Failed to convert tag {}: {}'.format(child.name, str(child)))
                self.unknown.convert(child)

        output = ''.join([unicode(child) for child in soup.descendants])

        pairs = [('&ldquo;', '``'), ('&rdquo;', '\'\''), ('&lsquo;', '`'), ('&rsquo;', '\'')]
        for find, rep in pairs:
            output = output.replace(find, rep)

        return output
        #return tex.replace('##LESSTHAN##', '<').replace('##GREATERTHAN##', '>')

    def _convertTag(self, tag):
        """
        Convert tag to latex.

        Args:
          tag[bs4.element.Tag]: The tag element to convert.
        """
        if isinstance(tag, bs4.element.Tag):
            for obj in self.elements:
                out = obj(tag)
                if out:
                    self.used.add(obj)
                    return out
        return None

    def preamble(self):
        """
        Return the latex preamble content.
        """

        output = []

        for obj in self.used:
            preamble = obj.preamble()
            if not isinstance(preamble, list):
                log.error("The preamble method of {} must return a list.".format(obj.__class__.__name__))
            for p in preamble:
                if p not in output:
                    output.append(p)

        return '\n'.join(output)
