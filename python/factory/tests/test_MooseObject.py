#!/usr/bin/env python3
import unittest
import factory

class TestObject(factory.MooseObject):
    @staticmethod
    def validParams():
        params = factory.MooseObject.validParams()
        params.add("this", default=1)
        return params


class TestMooseObject(unittest.TestCase):
    def testInit(self):
        mo = factory.MooseObject()
        self.assertEqual(mo.name(), None)

        mo = factory.MooseObject(name='test')
        self.assertEqual(mo.name(), 'test')

        to = TestObject()
        self.assertEqual(to.getParam('this'), 1)

        to = TestObject(this=2)
        self.assertEqual(to.getParam('this'), 2)

    def testIsParamValid(self):
        mo = factory.MooseObject()
        self.assertFalse(mo.isParamValid('name'))

        mo = factory.MooseObject(name='test')
        self.assertTrue(mo.isParamValid('name'))

    def testGetParam(self):
        mo = factory.MooseObject()
        self.assertEqual(mo.getParam('name'), None)

        mo = factory.MooseObject(name='test')
        self.assertEqual(mo.getParam('name'), 'test')

if __name__ == '__main__':
    unittest.main(module=__name__, verbosity=2, buffer=True)
