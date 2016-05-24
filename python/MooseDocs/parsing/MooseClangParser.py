import os
import re


import clang.cindex
clang.cindex.Config.set_library_path(os.getenv('MOOSE_CLANG_LIB'))



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
        includes = ['-x', 'c++', '-std=c++11']
        includes += ['-I' + os.path.dirname(self._header)]

        """
        includes.append('-I' + base_dir)
        for root, dirs, files in os.walk(base_dir):
            for d in dirs:
                includes.append('-I' + os.path.join(root, d))
        """
        # Build clang translation unit
        index = clang.cindex.Index.create()
        if self._source:
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
            print ' '*4*level, c.kind, c.spelling, c.extent.start.file, c.extent.start.line
            if recursive and c.get_children():
                self.dump(level+1, cursor=c)

    @staticmethod
    def _content(cursor):
        source_range = cursor.extent
        fid = open(source_range.start.file.name, 'r')
        content = fid.read()[source_range.start.offset:source_range.end.offset]
        fid.close()
        return content


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

        output = []
        self._getCursorHelper(self._translation_unit.cursor, output, kind, name)
        return output


    @staticmethod
    def _getCursorHelper(cursor, output, kind, name):

        for c in cursor.get_children():
            if c.kind == kind and (name == None or c.spelling == name):
                output.append(c)
            MooseClangParser._getCursorHelper(c, output, kind, name)



if __name__ == '__main__':

    src = '/Users/slauae/projects/moose/framework/src/kernels/Diffusion.C'
    parser = MooseClangParser(src)

 #   parser.dump()

    #    for child in parser._translation_unit.cursor.get_children():
#        print child
    cursors = parser._getCursor('CXX_METHOD', name='computeQpResidual')
    for c in cursors:
        print c.get_definition()

        """
        #print '\n'.join(dir(c))
        #break
        filename = str(c.extent.start.file)
        print filename

        fid = open(filename)
        lines = fid.readlines()
        fid.close()

        print c.extent.start.line, c.extent.end.line
        content = lines[c.extent.start.line-1:c.extent.end.line]
        print content
        """
