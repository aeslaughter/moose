"""Developer tools for MooseDocs."""
import os
import re
import importlib
import logging

import moosedown
from moosedown.tree import tokens
from moosedown.base import components, renderers, testing
from moosedown.extensions import command

LOG = logging.getLogger(__name__)

def command_line_options(subparser):
    """Define the 'devel' command."""
    devel_parser = subparser.add_parser('devel', help='Developer tools for MooseDocs.')
    devel_parser.add_argument('--generate-extension-tests', type=str,
                              help='Generate the test files for the supplied extension.')
    devel_parser.add_argument('--extension-dir', type=str, default='moosedown.extensions',
                              help='Directory containing the extension')


SUB_RE = re.compile(r'\<(?P<key>[A-Z]+)\>')
def sub_function(match, values):
    key = match.group('key')
    return values[key]

def main(options):

    # Module
    name = options.generate_extension_tests
    ext_dir = options.extension_dir
    mod_name = '{}.{}'.format(ext_dir, name)
    mod = importlib.import_module(mod_name)

    # Output
    output = os.path.join(os.getcwd(), 'test', 'extensions', 'test_{}.py'.format(name))

    # Tokens
    token_objects = testing.get_parent_objects(mod, tokens.Token)

    # Reader
    reader_objects = testing.get_parent_objects(mod, command.CommandComponent)
    reader_objects += testing.get_parent_objects(mod, components.TokenComponent)

    # Render
    render_objects = testing.get_parent_objects(mod, components.RenderComponent)

    # Exit if file exists
    if os.path.exists(output):
        LOG.error('The test file exists: %s.', output)
        #sys.exit(1)

    # Open file for writting
    fid = open(output, 'w')

    # Header
    items = dict(EXTENSION=mod_name, EXTENSIONROOT=ext_dir, EXTENSIONNAME=name)
    func = lambda m: sub_function(m, items)
    fid.write(SUB_RE.sub(func, HEAD))

    # Tokens
    fid.write(TOKEN_HEAD)
    for obj in token_objects:
        func = lambda m: sub_function(m, dict(NAME=obj[0], EXTENSION=mod_name))
        fid.write(SUB_RE.sub(func, TOKEN_TEST))

    # Tokenize Tests
    fid.write("\n# TOKENIZE TESTS")
    for obj in reader_objects:
        func = lambda m: sub_function(m, dict(NAME=obj[0], BASE="testing.MooseDocsTestCase"))
        fid.write(SUB_RE.sub(func, TOKENIZE))

    # Render Tests
    fid.write("\n# RENDERER TESTS")
    for obj in render_objects:
        for renderer in RENDERERS:
            items = dict(NAME=obj[0],
                         NODE="",
                         RENDERER=renderer,
                         SUFFIX=renderer.replace('Renderer', ''))
            if renderer == 'MaterializeRenderer':
                items['TEXT'] = ""
                items['BASE'] = 'Test<NAME>HTML'.replace('<NAME>', obj[0])

            else:
                items['TEXT'] = "\n    TEXT = u'ENTER TEXT HERE'"
                items['BASE'] = "testing.MooseDocsTestCase"

            if renderer == 'LatexRenderer':
                items['NODE'] = LATEX_NODE
            elif renderer == 'HTMLRenderer':
                items['NODE'] = HTML_NODE

            func = lambda m: sub_function(m, items)
            fid.write(SUB_RE.sub(func, RENDER))

    # Finish
    fid.write(FOOT)
    fid.close()


RENDERERS = ['HTMLRenderer', 'MaterializeRenderer', 'LatexRenderer']

HEAD="""#!/usr/bin/env python
\"\"\"Testing for <EXTENSION> MooseDocs extension.\"\"\"
import unittest
from <EXTENSIONROOT> import <EXTENSIONNAME>
from moosedown.tree import tokens, html, latex
from moosedown.base import testing, renderers
"""

TOKENIZE="""
class Test<NAME>Tokenize(<BASE>):
    \"\"\"Test tokenization of <NAME>\"\"\"
    def testToken(self):
        pass
"""

RENDER="""
class Test<NAME><SUFFIX>(<BASE>):
    \"\"\"Test renderering of <NAME> with <RENDERER>\"\"\"

    RENDERER = renderers.<RENDERER><TEXT>
    <NODE>
    def testTree(self):
        node = self.node()

    def testWrite(self):
        node = self.node()
        html = node.write()
"""

HTML_NODE="""
    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')
"""

LATEX_NODE="""
    def node(self):
        return self.render(self.TEXT).find('document')
"""

FOOT="""
if __name__ == '__main__':
    unittest.main(verbosity=2)
"""

TOKEN_HEAD="""
# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    \"\"\"Test Token object for <EXTENSION> MooseDocs extension.\"\"\"
"""

TOKEN_TEST="""
    def test<NAME>(self):
        pass
"""
