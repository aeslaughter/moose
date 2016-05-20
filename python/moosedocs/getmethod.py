#!/usr/bin/env python
import clang.cindex
clang.cindex.Config.set_library_path('/opt/moose/llvm-3.7.0/lib')

def getCursors(cursor, output, kind):
    """
    Recursively extract all the cursors of the given kind.
    """
    for c in cursor.get_children():
        if c.kind == kind:
            output.append(c)
        getCursors(c, output, kind)

if __name__ == '__main__':

    # Parse the test file
    index = clang.cindex.Index.create()
    tu = index.parse('method.C', ['-x', 'c++'])

    # Extract the parsers
    output = []
    getCursors(tu.cursor, output, clang.cindex.CursorKind.CXX_METHOD)

    # Print the method declarations (How to I get the definitions?)
    for c in output:
        defn = c.get_definition() # Gives nothing
        print c.extent.start.file, c.extent.start.line, c.extent.end.line
