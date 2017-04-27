#!/usr/bin/env python
import os
import bs4
import unittest
from MooseDocs.testing import MarkdownTestCase
from MooseDocs.commands.MooseDocsMarkdownNode import MooseDocsMarkdownNode

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
        node = MooseDocsMarkdownNode(name='test', md_file='input.md', parser=cls.parser, site_dir=cls.WORKING_DIR)
        node.build()

        with open(node.url(), 'r') as fid:
            html = fid.read()
        cls.soup = bs4.BeautifulSoup(html, "html.parser")

    def testContent(self):

        self.assertIsNotNone(self.soup.find('h2'))

#class TestRequiredError(MarkdownTestCase):
#    EXTENSIONS = ['MooseDocs.extensions.template', 'meta']
#
#    def testError()



if __name__ == '__main__':
    unittest.main(verbosity=2)
