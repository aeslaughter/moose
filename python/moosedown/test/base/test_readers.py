#!/usr/bin/env python
import unittest
import mock

from moosedown.base import Reader, RecursiveLexer


class TestReader(unittest.TestCase):
    """
    Test basic functionality and error handling of Reader objects.
    """
    def testConstruction(self):
        """
        Test most basic construction.
        """
        reader = Reader(RecursiveLexer('foo'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
