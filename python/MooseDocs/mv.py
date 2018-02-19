import os
import subprocess
import re

import anytree

import MooseDocs
from MooseDocs.tree import syntax, app_syntax

exe = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
root = app_syntax(exe)

group = 'Framework'
prefix = 'documentation/systems'

old_dir = 'docs/content'
new_dir = '{}/doc/content'.format(group.lower())


def update(filename):
    with open(filename, 'r') as fid:
        content = fid.read()

    content = re.sub(r'^(#+.*?)$', r'\1\n', content, flags=re.MULTILINE)

    with open(filename, 'w') as fid:
        content = fid.write(content)



if __name__ == '__main__':

    markers = anytree.search.find(root, filter_=lambda n: n.fullpath == '/Adaptivity/Markers')
    print markers

    for child in markers:
        new = None; old = None
        if group in child.groups:
            md = child.markdown(prefix)
            new = os.path.join(MooseDocs.MOOSE_DIR, new_dir, md)
            if isinstance(child, syntax.SyntaxNode):
                old = os.path.join(MooseDocs.MOOSE_DIR, old_dir, md)

            elif isinstance(child, syntax.ObjectNode):
                x = md.split('/')
                x.insert(-1, group.lower())
                old = os.path.join(MooseDocs.MOOSE_DIR, old_dir, *x)

            loc = os.path.dirname(new)
            if not os.path.exists(loc):
                os.makedirs(loc)
            print "{}:\n    OLD: {}\n    NEW: {}\n".format(child.name, old, new)
            #subprocess.call(['git', 'mv', old, new])

            subprocess.call(['cp', old, new])
            update(new)
