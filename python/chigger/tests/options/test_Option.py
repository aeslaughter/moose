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
        found = False
        for match in re.finditer(r'WARNING\s*\n(?P<message>.*?)(?=^\n|\Z)', output, flags=re.MULTILINE|re.DOTALL):
            found = True
            self.assertIn(msg, match.group('message'))

        if not found:
            self.assertTrue(False, "No warnings exist.")

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
        self.assertInWarning("Attempting to set 'foo' to a value of 4 but only the following are allowed: (1, 'two')")

    def testType(self):
        opt = Option('foo', vtype=int)
        self.assertIsNone(opt.default)
        self.assertIsNone(opt.value)

        opt.value = 1
        self.assertEqual(opt.value, 1)

        opt.value = 4.
        self.assertInWarning("'foo' must be of type <type 'int'> but <type 'float'> provided.")
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
        self.assertInWarning("Attempting to set 'foo' to a value of 4 but only the following are allowed: (1, 2)")
        self.assertEqual(opt.value, 1)

    def testAllowWithTypeError(self):

        with self.assertRaises(TypeError) as e:
            Option('foo', allow='wrong')
        self.assertIn("The supplied 'allow' argument must be a 'tuple', but <type 'str'> was provided.", e.exception.message)

        with self.assertRaises(TypeError) as e:
            Option('foo', vtype=int, allow=(1,'2'))
        self.assertIn("The supplied 'allow' argument must be a 'tuple' of <type 'int'> items, but a <type 'str'> item was provided.", e.exception.message)

    def testApply(self):

        opt = Option('foo', default=42)
        self.assertFalse(opt.applied)
        self.assertEqual(opt.apply(), 42)
        self.assertEqual(opt.value, 42)
        self.assertTrue(opt.applied)
        opt.value = 42
        self.assertTrue(opt.applied)
        opt.value = 43
        self.assertEqual(opt.value, 43)
        self.assertFalse(opt.applied)
        self.assertEqual(opt.apply(), 43)
        self.assertEqual(opt.value, 43)
        self.assertTrue(opt.applied)

    def testArray(self):
        opt = Option('foo', default=(1,2))
        self.assertEqual(opt._Option__array, True)
        self.assertEqual(opt.value, (1,2))

        opt.value = 4
        self.assertInWarning("'foo' was defined as an array, which require <type 'tuple'> for assignment, but a <type 'int'> was provided.")

        opt.value = (3, 4)
        self.assertEqual(opt.value, (3,4))

        opt.value = ('1', )
        self.assertEqual(opt.value, ('1',))

        opt = Option('foo', vtype=int, array=True)
        self.assertEqual(opt._Option__array, True)
        self.assertIsNone(opt.value)

        opt.value = 4
        self.assertInWarning("'foo' was defined as an array, which require <type 'tuple'> for assignment, but a <type 'int'> was provided.")

        opt.value = ('1', )
        self.assertInWarning("The values within 'foo' must be of type <type 'int'> but <type 'str'> provided.")
        self.assertIsNone(opt.value)

        opt.value = (1, )
        self.assertEqual(opt.value, (1,))

    def testDoc(self):
        opt = Option('foo', doc='This is foo, not bar.')
        self.assertEqual(opt.doc, 'This is foo, not bar.')

        opt = Option('foo', doc=u'This is foo, not bar.')
        self.assertEqual(opt.doc, u'This is foo, not bar.')

        with self.assertRaises(TypeError) as e:
            Option('foo', doc=42)
        self.assertIn("The supplied 'doc' argument must be a 'str' or 'unicode', but <type 'int'> was provided.", e.exception.message)

    def testName(self):
        opt = Option('foo')
        self.assertEqual(opt.name, 'foo')

        opt = Option(u'foo')
        self.assertEqual(opt.name, u'foo')

        with self.assertRaises(TypeError) as e:
            Option(42)
        self.assertIn("The supplied 'name' argument must be a 'str' or 'unicode', but <type 'int'> was provided.", e.exception.message)

    def testPrint(self):

        opt = Option('foo',
                     default=27,
                     allow=tuple(range(1,42)),
                     vtype=int,
                     doc="This option is not bar, but this description is long to test that it gets wrapped at 80 characters.")
        print opt
        out = sys.stdout.getvalue()
        self.assertIn('foo', out)
        self.assertIn('Value:   27', out)
        self.assertIn('Default: 27', out)
        self.assertIn('Array:   False', out)
        self.assertIn("Type:    <type 'int'>", out)
        self.assertIn("Applied: False", out)
        self.assertIn('Allow:   (1, 2', out)



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
