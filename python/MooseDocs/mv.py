import os
import subprocess
import shutil
import logging

import MooseDocs
from MooseDocs.MooseMarkdown import MooseMarkdown
from MooseDocs.extensions.app_syntax import AppSyntaxExtension

app = 'framework'
source_root = '/Users/slauae/projects/moosedown/docs/content/documentation/systems'

logging.basicConfig()
config = MooseDocs.load_config('/Users/slauae/projects/moosedown/docs/website.yml')
parser = MooseMarkdown(config)
ext = parser.getExtension(AppSyntaxExtension)
syntax = ext.getMooseAppSyntax()


for node in syntax.findall():
    src = os.path.join(source_root, node.markdown('', absolute=False))

    group = node.groups.keys()[0]
    if group == 'framework':
        destination_root = '/Users/slauae/projects/moosedown/{}/doc/content/documentation/systems'
    else:
        destination_root = '/Users/slauae/projects/moosedown/modules/{}/doc/content/documentation/systems'

    if os.path.isfile(src):
        dst = node.markdown('', absolute=False).replace('/{}/'.format(group), '/')
        dst = os.path.join(destination_root.format(group), dst)
        cmd = ['git', 'mv', src, dst]

        if os.path.isfile(dst):
            os.remove(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst)

        dst_dir = os.path.dirname(dst)
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)

        #print ' '.join(cmd)
        subprocess.call(cmd)
