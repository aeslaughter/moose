#!/usr/bin/env python
"""Testing for common.parse_settings function."""
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
        known, unknown = common.parse_settings(defaults, raw)
        self.assertEqual(known['year'], 2003)
        self.assertNotIn('month', known)
        self.assertIn('month', unknown)
        self.assertEqual(unknown['month'], 'june')

if __name__ == '__main__':
    unittest.main(verbosity=2)
