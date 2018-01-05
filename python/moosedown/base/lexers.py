import collections
import logging
import traceback

import moosedown
from moosedown import tree, common
from Grammer import Grammer

LOG = logging.getLogger(__name__)

class Lexer(object):
    def __init__(self):
        self._node = None

    def tokenize(self, text, parent, grammer, line=1, node=None):

        #if node is None:
        #    node = parent.node

        #text = node.content

        if not isinstance(text, unicode):
            raise TypeError("The supplied text to the lexer must be of type 'unicode' but '{}' was provided.".format(type(text).__name__))

        #TODO: "text" should be required to be a node and self._node should be removed
        #if isinstance(text, moosedown.tree.page.PageNodeBase):
            #self._node = text
        #    text = text.content
            #TODO: test for None
        n = len(text)
        pos = 0
        mo, pattern = self._search(text, grammer, pos)
        while (mo is not None) and (pos < n): # pos < n is needed to avoid empty string

            #TODO: move exception handling to here (except common.TokenizeException)
            try:
                obj = self.buildObject(pattern, mo, parent, line, node)
            except Exception as e:
                obj = tree.tokens.Exception(parent, match=mo, pattern=pattern, line=line,
                                            traceback=traceback.format_exc())

            obj.line = line #
            obj.match = mo
            obj.node = node

            line += mo.group(0).count('\n')
            pos = mo.end()
            mo, pattern = self._search(text, grammer, pos)

        if pos < n: #TODO: exception
            obj = tree.tokens.Exception(parent, match=mo, pattern=pattern, line=line)#content=text[pos:])
            obj.line = line #
            obj.match = mo
            obj.node = node

    def _search(self, text, grammer, position=0):
        for pattern in grammer:
            m = pattern.regex.match(text, position)
            if m:
                return m, pattern
        return None, None

    def buildObject(self, pattern, match, parent, line, node):
        #parent.node = node #TODO: is there a better way
        obj = pattern.function(match, parent)


        #TODO: test obj is correct type and not None (None case just use parent?)

        # Set the line and regex match for error reporting within Renderers.

        # TODO: This should be handled at RecursiveLexer level
        #if self._node and self._node.source:
        #    obj.source = self._node.source

        return obj

class RecursiveLexer(Lexer):
    def __init__(self, base, *args):
        super(RecursiveLexer, self).__init__()
        self._grammers = collections.OrderedDict()
        self._grammers[base] = Grammer()
        for name in args:
            self._grammers[name] = Grammer()

    def tokenize(self, text, parent, grammer=None, line=1, node=None):
        if grammer is None:
            grammer = self._grammers[self._grammers.keys()[0]]
        super(RecursiveLexer, self).tokenize(text, parent, grammer, line, node)

    def grammer(self, group=None):
        if group is None:
            group = self._grammers.keys()[0]
        return self._grammers[group]

    def grammers(self):
        return self._grammers

    def add(self, group, *args):
        self.grammer(group).add(*args)

    def buildObject(self, pattern, match, parent, line, node):
        obj = super(RecursiveLexer, self).buildObject(pattern, match, parent, line, node)
        for key, value in self._grammers.iteritems():
            if key in match.groupdict():
                text = match.group(key)
                if text is not None:
                    self.tokenize(text, obj, value, line, node)
        return obj
