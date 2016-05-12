import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import os
import re

import clang.cindex
clang.cindex.Config.set_library_path(os.getenv('MOOSE_CLANG_LIB'))

MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getenv('HOME'), 'projects', 'moose'))


class MooseClangParser(object):
    """
    """

    READ_SUCCESSFUL = 0
    READ_FAILED = 1

    def __init__(self, filename):

        # Define the read status (assume failed)
        self._status = self.READ_FAILED

        # Define the header and source files
        self._source = None
        self._header = None
        if filename.endswith('.C'):
            self._source = filename
            self._header = self._source.replace('/src/', '/include/').replace('.C', '.h')
        elif filename.endswith('.h'):
            self._header = filename
            self._source = self._header.replace('/include/', '/src/').replace('.h', '.C')
        else:
            return

        # Check that at least the header exists
        if not os.path.exists(self._source):
            self._source = None
        if not os.path.exists(self._header):
            self._header = None
        if (self._header == None) and (self._source == None):
            return

        # Determine the root directory
        match = re.search(r'(.*?\/include)\/', self._header)
        base_dir = match.group(1)

        # Build the list of all headers in moose/framework
        includes = []
        includes.append('-I' + base_dir)
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                includes.append('-I' + os.path.join(root, d))

        # Build clang translation unit
        index = clang.cindex.Index.create()
        if self._source:
            print self._source
            print self._header
            self._translation_unit = index.parse(self._source, includes)
        else:
            self._translation_unit = index.parse(self._header, includes)

        self._status = self.READ_SUCCESSFUL

    def status(self):
        return self._status

    def method(self, name):

        print type(self._content)
        return ''.join(self._content[35:40])

    def dump(self, level = 0, **kwargs):
        cursor = kwargs.pop('cursor', self._translation_unit.cursor)
        recursive = kwargs.pop('recursive', True)
        for c in cursor.get_children():
            print ' '*4*level, c.kind, c.spelling
            if recursive and c.get_children():
                self.dump(level+1, cursor=c)

    def _getCursor(self, kind, **kwargs):
        """
        Locate the clang.cindex.Cursor object. (public)

        Args:
            kind[str]: The type of cursor (see clang.cindex.py) to locate (as a string)

        Kwargs:
            name[str]: The name of the cursor to return (i.e., Cursor.spelling)

        Returns:
            A list of all cursors matching the kind and optionally the name.
        """
        output = []
        name = kwargs.pop('name', None)
        kind = eval('clang.cindex.CursorKind.' + kind.upper())
        for c in self._translation_unit.cursor.get_children():
            if c.kind == kind:# and (name == None or c.spelling == name):
                output.append(c)
        return output


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

        parser = MooseClangParser(filename)
        el = etree.Element('pre')
        code = etree.SubElement(el, 'code')
        code.set('class', 'c++')
        code.text = parser.method(match.group(3))
        return el



class MooseMarkdown(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('moose_source', MooseSourcePattern(), '_begin')


def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':

    src = '/Users/slauae/projects/moose/framework/src/kernels/Diffusion.C'

    parser = MooseClangParser(src)

    parser.dump()
#    for child in parser._translation_unit.cursor.get_children():
#        print child
#    c = parser._getCursor('CXX_METHOD')
#    print c

    #md = markdown.Markdown(extensions=[MooseMarkdown()])
    #md.convertFile(input='/Users/slauae/projects/moose/docs/documentation/moose_style_markdown.md')
