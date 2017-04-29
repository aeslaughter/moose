#!/usr/bin/env python
import os
import bs4
import unittest
import mooseutils
from MooseDocs.testing import MarkdownTestCase
from MooseDocs.commands.MarkdownNode import MarkdownNode

class TestTemplate(MarkdownTestCase):
    """
    Test that misc extension is working. command is work.
    """
    EXTENSIONS = ['MooseDocs.extensions.template', 'MooseDocs.extensions.app_syntax', 'meta']

    @classmethod
    def updateExtensions(cls, configs):
        """
        Method to change the arguments that come from the configuration file for
        specific tests.  This way one can test optional arguments without permanently
        changing the configuration file.
        """
        configs['MooseDocs.extensions.template']['template'] = 'testing.html'

    @classmethod
    def setUpClass(cls):
        """
        Convenience function for converting markdown to html.
        """
        super(TestTemplate, cls).setUpClass()
        node = MarkdownNode(name='test', markdown='input.md', parser=cls.parser, site_dir=cls.WORKING_DIR)
        node.build()

        with open(node.url(), 'r') as fid:
            cls.html = fid.read()
        cls.soup = bs4.BeautifulSoup(cls.html, "html.parser")

    def testContent(self):
        self.assertIsNotNone(self.soup.find('h2'))
        self.assertIn('More Content', self.html)

if __name__ == '__main__':
    unittest.main(verbosity=2)
