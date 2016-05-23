#!/usr/bin/env python
import os, sys
sys.path.append('/opt/moose/llvm-3.7.0/bindings/python/')
import clang.cindex

#clang.cindex.Config.set_library_path('/opt/moose/llvm-3.7.0/lib')
clang.cindex.Config.set_library_path('/Library/Developer/CommandLineTools/usr/lib')

import clang.cindex
from clang.cindex import *

def method_definitions(cursor):
    for i in cursor.walk_preorder():
        print i.kind, i.is_definition(), i.get_definition()
        if i.kind != CursorKind.CXX_METHOD:
            continue
        if not i.is_definition():
            continue
        yield i

def extract_definition(cursor):
    filename = cursor.location.file.name
    with open(filename, 'r') as fh:
        contents = fh.read()
    return contents[cursor.extent.start.offset: cursor.extent.end.offset]

idx = Index.create()
tu = idx.parse('method.C', ['-x', 'c++'])
defns = method_definitions(tu.cursor)
for defn in defns:
    print extract_definition(defn)

"""
def getCursors(cursor, output, kind):
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
        print c, c.is_definition()
        defn = c.get_definition() # Gives nothing
        print c.extent.start.file, c.extent.start.line, c.extent.end.line
"""
