#!/usr/bin/env python
import re
import os
import unittest
import tempfile
import pickle, cPickle

import MooseDocs
from MooseDocs import common
from MooseDocs.tree import base, tokens
from MooseDocs.base import lexers, components, testing

def do_pickle(obj):
    tmp = tempfile.mkstemp(prefix='tmp', suffix='.pickle')[1]
    with open(tmp, 'w') as fid:
        pickle.dump(obj, fid, pickle.HIGHEST_PROTOCOL)
    with open(tmp, 'r') as fid:
        p = pickle.load(fid)
    os.remove(tmp)
    return p

def do_c_pickle(obj):
    tmp = tempfile.mkstemp(prefix='tmp', suffix='.pickle')[1]
    with open(tmp, 'w') as fid:
        cPickle.dump(obj, fid, pickle.HIGHEST_PROTOCOL)
    with open(tmp, 'r') as fid:
        p = cPickle.load(fid)
    return p


class TestPickle(unittest.TestCase):


    def testProperty(self):
        prop = tokens.Property('foo', default=1, ptype=int, required=False)
        pick = do_pickle(prop)

        self.assertEqual(prop.name, pick.name)
        self.assertEqual(prop.default, pick.default)
        self.assertEqual(prop.type, pick.type)
        self.assertEqual(prop.required, pick.required)

    def testNodeBase(self):
        node = base.NodeBase(None, 'name', foo=42)
        pick = do_pickle(node)

        self.assertEqual(node.name, pick.name)
        self.assertEqual(node.parent, pick.parent)
        self.assertEqual(node.attributes, pick.attributes)

        self.assertIn('foo', node)
        self.assertIn('foo', pick)

        self.assertEqual(node['foo'], 42)
        self.assertEqual(pick['foo'], 42)

    def testNodeBaseWithProperty(self):
        node = tokens.Token(None, recursive=False)
        pick = do_pickle(node)

        self.assertFalse(node.recursive)
        self.assertFalse(pick.recursive)

    def testNodeTree(self):
        root = tokens.Token(None, recursive=False)
        tokens.Token(root)
        pick = do_pickle(root)

        self.assertFalse(root.recursive)
        self.assertFalse(pick.recursive)

        self.assertTrue(root(0).recursive)
        self.assertTrue(pick(0).recursive)

    @unittest.skip("Not possible.")
    def testPattern(self):
        comp = components.TokenComponent()

        regex = re.compile(r'foo')
        pattern = lexers.Pattern('foo', regex, comp)
        pick = do_pickle(pattern)

        self.assertEqual(pattern.name, pick.name)
        self.assertEqual(pattern.regex, pick.regex)
        self.assertIs(pattern.function, pick.function)

class TestPickleAST(testing.MooseDocsTestCase):
    EXTENSIONS = [MooseDocs.extensions.core]

    def testAST(self):
        ast = self.ast(u'*=+~strike~ bold+ under= emphasis*')
        self.assertIsInstance(ast(0), tokens.Paragraph)
        self.assertIsInstance(ast(0)(0), tokens.Emphasis)
        self.assertIsInstance(ast(0)(0)(0), tokens.Underline)
        self.assertIsInstance(ast(0)(0)(0)(0), tokens.Strong)
        self.assertIsInstance(ast(0)(0)(0)(0)(0), tokens.Strikethrough)

        pick = do_pickle(ast)

        self.assertIsInstance(pick(0), tokens.Paragraph)
        self.assertIsInstance(pick(0)(0), tokens.Emphasis)
        self.assertIsInstance(pick(0)(0)(0), tokens.Underline)
        self.assertIsInstance(pick(0)(0)(0)(0), tokens.Strong)
        self.assertIsInstance(pick(0)(0)(0)(0)(0), tokens.Strikethrough)

    def testAlert(self):
        filename = os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'content', 'utilities', 'MooseDocs', 'alert.md')
        content = common.read(filename)
        ast = tokens.Token(None)
        self._reader.parse(ast, content)

        import time
        start = time.time()
        pick = do_pickle(ast)
        end = time.time()
        print end - start

        start = time.time()
        pick = do_c_pickle(ast)
        end = time.time()
        print end - start


if __name__ == '__main__':
    unittest.main(verbosity=2)
