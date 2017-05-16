#!/usr/bin/env python
#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################

import unittest
import bs4

import MooseDocs
from MooseDocs.testing import MarkdownTestCase
from MooseDocs.commands.MarkdownNode import MarkdownNode

class TestTemplate(MarkdownTestCase):
    EXTENSIONS = ['MooseDocs.extensions.template', 'MooseDocs.extensions.app_syntax', 'meta']

    @classmethod
    def updateExtensions(cls, configs):
        """
        Method to change the arguments that come from the configuration file for
        specific tests.  This way one can test optional arguments without permanently
        changing the configuration file.
        """
        configs['MooseDocs.extensions.template']['template'] = 'testing.html'
        configs['MooseDocs.extensions.app_syntax']['hide']['framework'].append('/Functions')
        configs['MooseDocs.extensions.app_syntax']['hide']['phase_field'].append('/ICs')

    @classmethod
    def setUpClass(cls):
        super(TestTemplate, cls).setUpClass()

        # Use BoxMarker.md to test Doxygen and Code lookups
        node = MarkdownNode(name='BoxMarker', markdown='input.md', parser=cls.parser,
                            site_dir=cls.WORKING_DIR)
        node.build()

        with open(node.url(), 'r') as fid:
            cls.html = fid.read()
        cls.soup = bs4.BeautifulSoup(cls.html, "html.parser")

    def testContent(self):
        self.assertIsNotNone(self.soup.find('h2'))
        self.assertIn('More Content', self.html)

    def testDoxygen(self):
        a = self.soup.find('a')
        self.assertIsNotNone(a)
        self.assertIn('classBoxMarker.html', str(a))
        self.assertIn('Doxygen', str(a))

    def testCode(self):
        html = str(self.soup)
        self.assertIn('href="https://github.com/idaholab/moose/blob/master/framework/include/'\
                      'markers/BoxMarker.h"', html)
        self.assertIn('href="https://github.com/idaholab/moose/blob/master/framework/src/'\
                      'markers/BoxMarker.C"', html)

    def testHidden(self):
        md = '!syntax objects /Functions'
        html = self.convert(md)
        gold = '<a class="moose-bad-link" data-moose-disable-link-error="1" ' \
               'href="{}/docs/content/documentation/systems' \
               '/Functions/framework/ParsedVectorFunction.md">ParsedVectorFunction</a>'
        self.assertIn(gold.format(MooseDocs.MOOSE_DIR.rstrip('/')), html)

    def testPolycrystalICs(self):
        md = '[Foo](/ICs/PolycrystalICs/index.md)'
        html = self.convert(md)
        gold = '<a class="moose-bad-link" href="/ICs/PolycrystalICs/index.md">'
        self.assertIn(gold, html)

if __name__ == '__main__':
    unittest.main(verbosity=2)
