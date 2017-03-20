#!/usr/bin/env python
import os
import unittest
import MooseDocs
from MooseDocs.testing import MarkdownTestCase

class TestDevelExtension(MarkdownTestCase):
    """
    Test commands in MooseDocs devel extension.
    """
    def readGold(self, name):
        """
        The parsed markdown contains a path to ".../moose/docs/".
        This puts in the correct path after given the HTML that comes before
        and after the string "/Users/<username>/<intermediate_directories>/moose".
        """
        html = super(TestDevelExtension, self).readGold(name)
        for i, txt in enumerate(html):
            html[i] = txt.replace('<<CWD>>', os.path.abspath(os.path.join(MooseDocs.MOOSE_DIR, 'docs')))
        return html

    def testBuildStatus(self):
        md = '!buildstatus https://moosebuild.org/mooseframework/ float=right padding-left=10px'
        self.assertConvert('test_BuildStatus.html', md)

    def testPackage(self):
        md = '!MOOSEPACKAGE arch=centos7 return=link!'
        self.assertConvert('test_Package.html', md)

    def testConfig(self):
        md = '!extension DevelExtension'
        self.assertConvert('test_Config.html', md)

    def testSettings(self):
        md = '!extension-settings moose_extension_config'
        self.assertConvert('test_Settings.html', md)

if __name__ == '__main__':
    unittest.main(verbosity=2)
