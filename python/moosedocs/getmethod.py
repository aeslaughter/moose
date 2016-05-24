#!/usr/bin/env python
import clang.cindex
from clang.cindex import *
#clang.cindex.Config.set_library_path('/opt/moose/llvm-3.7.0/lib')
clang.cindex.Config.set_library_path('/Library/Developer/CommandLineTools/usr/lib')

def method_definitions(cursor):
    for i in cursor.walk_preorder():
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
