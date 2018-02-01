#!/usr/bin/env python
"""Testing for common.parse_settings function."""

import unittest
from moosedown import common

class TestParseSettings(unittest.TestCase):
    """
    Test the Storage object.
    """
    def testBasic(self):
        """
        Test setting a value.
        """
        defaults = dict(year=(1980, 'doc'), month=('june', 'doc'), day=(24, 'doc'))
        raw = 'year=2003'
        known, unknown = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 2003)
        self.assertEqual(known['month'], 'june')
        self.assertEqual(known['day'], 24)
        self.assertEqual(unknown, dict())

    def testSpace(self):
        """
        Test that values can have spaces.
        """
        defaults = dict(year=(1980, 'doc'), month=('june', 'doc'), day=(24, 'doc'))
        raw = 'year=the year I was born'
        known, _ = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 'the year I was born')

    def testFloat(self):
        """
        Test float conversion.
        """
        defaults = dict(year=(1980, 'doc'))
        raw = 'year=2003'
        known, _ = common.parse_settings(defaults, raw)
        self.assertIsInstance(known['year'], float)

    def testUnknown(self):
        """
        Test unknown key, value pairs.
        """
        defaults = dict(year=(1980, 'doc'))
        raw = 'year=2003 month=june'
        known, unknown = common.parse_settings(defaults, raw, error_on_unknown=False)
        self.assertEqual(known['year'], 2003)
        self.assertNotIn('month', known)
        self.assertIn('month', unknown)
        self.assertEqual(unknown['month'], 'june')

    def testUnknownException(self):
        """
        Test unknown key, value pairs with error exception
        """
        defaults = dict(year=(1980, 'doc'))
        raw = 'year=2003 month=june'
        with self.assertRaises(KeyError) as e:
            known, unknown = common.parse_settings(defaults, raw)

        self.assertIn("The following key, value settings are unknown:", e.exception.message)
        self.assertIn("month", e.exception.message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
