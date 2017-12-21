#!/usr/bin/env python
import unittest

#import moosedown
#from moosedown import extensions
#from moosedown.base import testing, TokenComponent, RenderComponent
from moosedown.base import testing# MarkdownExtension, RenderExtension

#import hit

class TestErrorHandling(testing.MarkdownTestCase):

    def testBasic(self):
        text = u'This is some text that contains a bad\n[link], it should error when rendered.'
        ast = self.render(text)
        print ast




if __name__ == '__main__':
    unittest.main(verbosity=2)
