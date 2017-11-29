import os
import subprocess
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
    group = node.groups.keys()[0]
    if group == 'framework':
        destination_root = '/Users/slauae/projects/moosedown/{}/doc/content/documentation/systems'
    else:
        destination_root = '/Users/slauae/projects/moosedown/modules/{}/doc/content/documentation/systems'

    src = node.markdown(source_root)
    dst = node.markdown('', absolute=False).replace('/{}/'.format(group), '/')
    dst = os.path.join(destination_root.format(group), dst)
    cmd = ['git', 'mv', src, dst]
    print ' '.join(cmd)
    #subprocess.call(cmd)
