"""Developer tools for MooseDocs."""
import os
import sys
import re
import importlib
import logging

import MooseDocs
from MooseDocs.tree import tokens
from MooseDocs.base import components, renderers, testing
from MooseDocs.extensions import command

LOG = logging.getLogger(__name__)

def command_line_options(subparser):
    """Define the 'devel' command."""
    devel_parser = subparser.add_parser('devel', help='Developer tools for MooseDocs.')
    devel_parser.add_argument('--generate-extension-tests', type=str,
                              help='Generate the test files for the supplied extension.')
    devel_parser.add_argument('--extension-dir', type=str, default='MooseDocs.extensions',
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
    reader_objects = set(testing.get_parent_objects(mod, command.CommandComponent))
    reader_objects.update(testing.get_parent_objects(mod, components.TokenComponent))

    # Render
    render_objects = testing.get_parent_objects(mod, components.RenderComponent)

    # Exit if file exists
    if os.path.exists(output):
        LOG.error('The test file exists: %s.', output)
        sys.exit(1)

    # Open file for writting
    fid = open(output, 'w')

    # Header
    items = dict(MODULE=mod_name, EXTENSIONROOT=ext_dir, EXTENSIONNAME=name)
    func = lambda m: sub_function(m, items)
    fid.write(SUB_RE.sub(func, HEAD))

    # Tokens
    func = lambda m: sub_function(m, dict(MODULE=mod_name))
    fid.write(SUB_RE.sub(func, TOKEN_HEAD))
    for obj in token_objects:
        func = lambda m: sub_function(m, dict(NAME=obj[0], MODULE=mod_name))
        fid.write(SUB_RE.sub(func, TOKEN_TEST))

    # Tokenize Tests
    fid.write("\n# TOKENIZE TESTS")
    for obj in reader_objects:
        func = lambda m: sub_function(m, dict(NAME=obj[0], MODULE=mod_name, BASE="testing.MooseDocsTestCase"))
        fid.write(SUB_RE.sub(func, TOKENIZE))

    # Render Tests
    fid.write("\n# RENDERER TESTS")
    for obj in render_objects:
        func = lambda m: sub_function(m, dict(NAME=obj[0], MODULE=mod_name, RENDERER="HTMLRenderer"))
        fid.write(SUB_RE.sub(func, HTML))

        func = lambda m: sub_function(m, dict(NAME=obj[0], MODULE=mod_name, RENDERER="MaterializeRenderer"))
        fid.write(SUB_RE.sub(func, MATERIALIZE))

        func = lambda m: sub_function(m, dict(NAME=obj[0], MODULE=mod_name, RENDERER="LatexRenderer"))
        fid.write(SUB_RE.sub(func, LATEX))

    # Finish
    fid.write(FOOT)
    fid.close()


RENDERERS = ['HTMLRenderer', 'MaterializeRenderer', 'LatexRenderer']

HEAD="""#!/usr/bin/env python
\"\"\"Testing for <MODULE> MooseDocs extension.\"\"\"
import unittest

import MooseDocs
from <EXTENSIONROOT> import <EXTENSIONNAME>
from MooseDocs.tree import tokens, html, latex
from MooseDocs.base import testing, renderers
"""

TOKENIZE="""
class Test<NAME>Tokenize(<BASE>):
    \"\"\"Test tokenization of <NAME>\"\"\"

    EXTENSIONS = [MooseDocs.extensions.core, <MODULE>]

    def testToken(self):
        self.assertFalse(True)
"""

HTML="""
class Test<NAME>HTML(testing.MooseDocsTestCase):
    \"\"\"Test renderering of <NAME> with <RENDERER>\"\"\"

    EXTENSIONS = [MooseDocs.extensions.core, <MODULE>]
    RENDERER = renderers.<RENDERER>
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('moose-content', attr='class')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")
"""

MATERIALIZE="""
class Test<NAME>Materialize(Test<NAME>HTML):
    \"\"\"Test renderering of <NAME> with <RENDERER>\"\"\"

    RENDERER = renderers.<RENDERER>
"""

LATEX="""
class Test<NAME>Latex(testing.MooseDocsTestCase):
    \"\"\"Test renderering of <NAME> with <RENDERER>\"\"\"

    EXTENSIONS = [MooseDocs.extensions.core, <MODULE>]
    RENDERER = renderers.<RENDERER>
    TEXT = u'TEST STRING HERE'

    def node(self):
        return self.render(self.TEXT).find('document')(0)

    def testTree(self):
        node = self.node()
        self.assertFalse(True)

    def testWrite(self):
        node = self.node()
        self.assertEqual(node.write(), "GOLD")
"""

FOOT="""
if __name__ == '__main__':
    unittest.main(verbosity=2)
"""

TOKEN_HEAD="""
# TOKEN OBJECTS TESTS
class TestTokens(unittest.TestCase):
    \"\"\"Test Token object for <MODULE> MooseDocs extension.\"\"\"

    EXTENSIONS = [MooseDocs.extensions.core, <MODULE>]
"""

TOKEN_TEST="""
    def test<NAME>(self):
        self.assertFalse(True)
"""
