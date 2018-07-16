#!/usr/bin/env python
import unittest

from MooseDocs import base
from MooseDocs.base import testing


class TestCoreFormat(testing.MooseDocsTestCase):
    RENDERER = base.MooseDownRenderer

    def testHeading(self):
        text = u"### Headings can be long, so long that they cross the line limit. In this case " \
               "the text should wrap around to a new line. It also must work with settings, the " \
               "settings should be aligned on a new line as well. class=testing id=heading-id"
        lines = self.render(text).write().split('\n')

        self.assertEqual(len(lines), 7)
        self.assertTrue(lines[0].startswith('### Headings'))
        self.assertTrue(lines[1].startswith('    around'))
        self.assertTrue(lines[2].startswith('    line'))
        self.assertTrue(lines[3].startswith('    id='))
        self.assertTrue(lines[4].startswith('    class='))
        self.assertEqual(lines[5], u'')
        self.assertEqual(lines[6], u'')

    def testHeading2(self):
        text = u"## A Short Heading id=a-short-heading"
        lines = self.render(text).write().split('\n')

        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], u'## A Short Heading')
        self.assertEqual(lines[1], u'   id=a-short-heading')
        self.assertEqual(lines[2], u'')
        self.assertEqual(lines[3], u'')


if __name__ == '__main__':
    unittest.main(verbosity=2)
