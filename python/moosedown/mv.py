import os
import logging

import MooseDocs
from MooseDocs.MooseMarkdown import MooseMarkdown
from MooseDocs.extensions.app_syntax import AppSyntaxExtension

app = 'framework'
source_root = '/Users/slauae/projects/moosedown/docs/content/documentation/systems'

if app == 'framework':
    destination_root = '/Users/slauae/projects/moosedown/{}/doc/content/documentation/systems'
else:
    destination_root = '/Users/slauae/projects/moosedown/modules/{}/doc/content/documentation/systems'
destination_root = destination_root.format(app)


logging.basicConfig()
config = MooseDocs.load_config('/Users/slauae/projects/moosedown/docs/website.yml')
parser = MooseMarkdown(config)
ext = parser.getExtension(AppSyntaxExtension)
syntax = ext.getMooseAppSyntax()


print syntax
