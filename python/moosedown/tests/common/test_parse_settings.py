#!/usr/bin/env python
import unittest
from MooseDocs import common

class TestParseSettings(unittest.TestCase):
    """
    Test the Storage object.
    """
    def testBasic(self):
        """
        """
        defaults = dict(year=(1980, 'doc'), month=('june', 'doc'), day=(24, 'doc'))
        raw = 'year=2003'
        known, unknown = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 2003)
        self.assertEqual(known['month'], 'june')
        self.assertEqual(known['day'], 24)
        self.assertEqual(unknown, dict())

    def testSpace(self):
        defaults = dict(year=(1980, 'doc'), month=('june', 'doc'), day=(24, 'doc'))
        raw = 'year=the year I was born'
        known, _ = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 'the year I was born')

    def testFloat(self):
        defaults = dict(year=(1980, 'doc'))
        raw = 'year=2003'
        known, _ = common.parse_settings(defaults, raw)
        self.assertIsInstance(known['year'], float)

    def testUnknown(self):
        defaults = dict(year=(1980, 'doc'))
        raw = 'year=2003 month=june'
        known, unknown = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 2003)
        self.assertNotIn('month', known)
        self.assertIn('month', unknown)
        self.assertEqual(unknown['month'], 'june')

if __name__ == '__main__':
    unittest.main(verbosity=2)
