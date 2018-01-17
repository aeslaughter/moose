import collections
import logging
import traceback

import moosedown
from moosedown import tree, common
from Grammer import Grammer

LOG = logging.getLogger(__name__)

class LexerInformation(object):
    #TODO: make these methods better __contains__ should do groupdict() stuff
    #      __get__ should call group
    #      __iter__ should loop groups
    #      createToken should be createToken(self, parent, info)
    #      createHTML should be self, parent, token
    #      node should change to page
    def __init__(self, match, pattern, node, line):
        self.match = match
        self.pattern = pattern
        self.node = node
        self.line = line

    def group(self, value=0):
        return self.match.group(value)
    def groups(self):
        return self.match.groups()
    def groupdict(self):
        return self.match.groupdict()


class Lexer(object):
    def __init__(self):
        self._node = None

    def tokenize(self, parent, grammer, text, node, line=1):

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

            #print pattern

            info = LexerInformation(mo, pattern, node, line)
            try:
                obj = self.buildObject(parent, info)
            except Exception as e:
                obj = tree.tokens.Exception(parent, info=info, traceback=traceback.format_exc()) #TODO: use info object
            #obj.line = line #
            #obj.match = mo
            #obj.node = node
            #obj.pattern = pattern

            line += mo.group(0).count('\n')
            pos = mo.end()
            mo, pattern = self._search(text, grammer, pos)


        if pos < n: #TODO: better exception
            print repr(text[pos:])
            #obj = tree.tokens.Exception(parent, match=mo, pattern=pattern, line=line)#content=text[pos:])
            #obj.line = line #
            #obj.match = mo
            #obj.node = node
            #obj.pattern = pattern

    def _search(self, text, grammer, position=0):
        for pattern in grammer:
            m = pattern.regex.match(text, position)
            if m:
                return m, pattern
        return None, None

    def buildObject(self, parent, info):
        obj = info.pattern.function(info, parent)
        obj.info = info #TODO: set ptype on base Token, change to info
        return obj

class RecursiveLexer(Lexer):
    def __init__(self, base, *args):
        Lexer.__init__(self)
        self._grammers = collections.OrderedDict()
        self._grammers[base] = Grammer()
        for name in args:
            self._grammers[name] = Grammer()

    #def tokenize(self, parent, grammer, text, node, line=1):
        #if grammer is None:
        #    grammer = self._grammers[self._grammers.keys()[0]]
    #    super(RecursiveLexer, self).tokenize(parent, grammer, text, node, line)

    def grammer(self, group=None):
        if group is None:
            group = self._grammers.keys()[0]
        return self._grammers[group]

    def grammers(self):
        return self._grammers

    def add(self, group, *args):
        self.grammer(group).add(*args)

    def buildObject(self, parent, info):
        obj = super(RecursiveLexer, self).buildObject(parent, info)
        for key, grammer in self._grammers.iteritems():
            if key in info.groupdict():
                text = info.group(key)
                if text is not None:
                    self.tokenize(obj, grammer, text, info.node, info.line)
        return obj
