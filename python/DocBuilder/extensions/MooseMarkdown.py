import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import os
import re

import clang.cindex


MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getenv('HOME'), 'projects', 'moose'))


class MooseCpp(object):
    """
    TODO: This should use clang-bindings
    """

    def __init__(self, filename):

        fid = open(filename, 'r')
        self._content = fid.readlines()
        fid.close()



    def method(self, name):

        print type(self._content)
        return ''.join(self._content[35:40])





class MooseSourcePattern(Pattern):

    CPP_RE = r'!\[(.*?)\]\((.*\.[Ch])\)'


    def __init__(self):
        Pattern.__init__(self, self.CPP_RE)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        filename = MOOSE_DIR.rstrip('/') + os.path.sep + match.group(3).lstrip('/')

        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('b')
            el.text = 'Invalid filename: ' + filename
            return el

        parser = MooseCpp(filename)
        el = etree.Element('code')
        el.text = parser.method(match.group(3))
        return el



class MooseMarkdown(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('moose_source', MooseSourcePattern(), '_begin')


def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':
    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(input='/Users/slauae/projects/moose/docs/documentation/moose_style_markdown.md')
