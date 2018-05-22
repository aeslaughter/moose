#!/usr/bin/env python2
#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import sys
import re
import unittest
from chigger.utils import Option

class TestOption(unittest.TestCase):

    def assertInWarning(self, msg):
        output = sys.stdout.getvalue()
        for match in re.finditer(r'WARNING\s*\n(?P<message>.*?)(?=^\n|\Z)', output, flags=re.MULTILINE|re.DOTALL):
            self.assertIn(msg, match.group('message'))

    def testMinimal(self):
        opt = Option('foo')
        self.assertEqual(opt.name, 'foo')
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

    def testValue(self):
        opt = Option('foo')
        self.assertEqual(opt.name, 'foo')
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

        self.value = 12345
        self.assertEqual(self.value, 12345)

    def testDefault(self):
        opt = Option('foo', default=12345)
        self.assertEqual(opt.name, 'foo')
        self.assertEqual(opt.default, 12345)
        self.assertEqual(opt.value, 12345)

        opt.value = '12345'
        self.assertEqual(opt.default, 12345)
        self.assertEqual(opt.value, '12345')

    def testAllow(self):
        opt = Option('foo', allow=(1, 'two'))
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

        opt.value = 1
        self.assertEqual(opt.value, 1)

        opt.value = 'two'
        self.assertEqual(opt.value, 'two')

        opt.value = 4
        self.assertInWarning("Attempting to set foo to a value of 4 but only the following are allowed: (1, 'two')")

    def testType(self):
        opt = Option('foo', vtype=int)
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

        opt.value = 1
        self.assertEqual(opt.value, 1)

        opt.value = 4.
        self.assertInWarning("foo must be of type int but float provided.")
        self.assertEqual(opt.value, 1)

    def testTypeWithAllow(self):

        opt = Option('foo', vtype=int, allow=(1,2))
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

        opt.value = 2
        self.assertEqual(opt.value, 2)

        opt.value = 1
        self.assertEqual(opt.value, 1)

        opt.value = 4
        self.assertInWarning("Attempting to set foo to a value of 4 but only the following are allowed: (1, 2)")
        self.assertEqual(opt.value, 1)


    def testAllowWithTypeError(self):

        with self.assertRaises(TypeError) as e:
            opt = Option('foo', vtype=int, allow=(1,'2'))

        self.assertIn("The supplied 'allow' argument must be a 'tuple' of <type 'int'> items, but a <type 'str'> item was provided.", e.exception.message)


if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True, exit=False)



"""
opt = chigger.utils.Options()

if args.type == 'run' or args.type == 'dump':
    opt.add('param', 1, 'Some parameter')
    opt.add('param2', 2, 'Some parameter', vtype=float)
    opt.add('param3', 3, 'A longer description that will be wrapped because it is so long. It needs to be long, really really long.', vtype=float, allow=[3,4,5,6,7,8,9,10])
    opt.add('param4', '1', 'Doc', allow=[1]) # implicit cast
    opt.add('param5', 'Doc')
    opt.add('param6', 3, 'Not long.', vtype=float, allow=[3,4,5,6,7,8,9,10])

    if args.type == 'dump':
        opt2 = chigger.utils.Options()
        opt2.add('item', 1, 'An item')
        opt2.add('item2', 2, 'An item')
        opt.add('sub', opt2, "A sub parameters")
        print opt

elif args.type == 'bad-type':
    opt.add('param', 'string', 'Doc', vtype=int)

elif args.type == 'bad-allow-type':
    opt.add('param', 1, 'Doc', allow=[[""]])

elif args.type == 'value-not-allowed':
    opt.add('param', 1, 'Doc', allow=[2,3])

elif args.type == 'bad-arg-count':
    opt.add('param')

elif args.type == 'duplicate':
    opt.add('param', 13, "A duplicate parameter")
    opt.add('param', 13, "A duplicate parameter")
"""
