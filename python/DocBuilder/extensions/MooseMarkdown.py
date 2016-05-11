import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import os
import re

#MULTI_RE = r'([*/_-]{2})(.*?)\2'
MULTI_RE = r'\[moose:\s+(.*?):(.*?)\]'

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

    #def getCompiledRegExp(self):
    #    regex = r'\[moose:\s+(.*?)\]'
    #    return re.compile(regex, flags=re.DOTALL|re.UNICODE)

    def handleMatch(self, match):

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        filename = MOOSE_DIR.rstrip('/') + os.path.sep + match.group(2).lstrip('/')

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
        md.inlinePatterns.add('moose_source', MooseSourcePattern(MULTI_RE), '_end')




if __name__ == '__main__':

    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(input='test.md')
