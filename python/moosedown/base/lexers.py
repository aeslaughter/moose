import collections
import logging
import traceback

import moosedown
from moosedown import tree, common
from Grammer import Grammer

LOG = logging.getLogger(__name__)

class LexerInformation(object): #TODO: TokenMetaData ???
    #TODO: make these methods better __contains__ should do groupdict() stuff
    #      __get__ should call group
    #      __iter__ should loop groups
    #      createToken should be createToken(self, parent, info)
    #      createHTML should be self, parent, token
    #      node should change to page
    def __init__(self, match=None, pattern=None, line=None):

        # TODO: make setters and getters that check types
        self.__match = match
        self.pattern = pattern
        self.line = line

    def __getitem__(self, value):
        return self.__match.group(value)

    def keys(self):
        return self.__match.groupdict().keys()

    def iteritems(self):
        for key, value in self.__match.groupdict().iteritems():
            yield key, value

    def __contains__(self, value):
        return value in self.__match.groupdict()

    def __str__(self):
        return 'line:{} match:{} pattern:{}'.format(self.line, self.__match, self.pattern)


class Lexer(object):
    def __init__(self):
        self._node = None

    def tokenize(self, parent, grammer, text, line=1):

        #if node is None:
        #    node = parent.node

        #text = node.content

        if not isinstance(text, unicode):
            raise TypeError("The supplied text to the lexer must be of type 'unicode' but '{}' was provided.".format(type(text).__name__))

        n = len(text)
        pos = 0
        while (pos < n):
            match = None
            for pattern in grammer:
                #print repr(text[pos:])
                match = pattern.regex.match(text, pos)
                if match:
                    info = LexerInformation(match, pattern, line)
                    try:
                        obj = self.buildObject(parent, info)
                    except Exception as e:
                        obj = tree.tokens.Exception(parent, info=info, traceback=traceback.format_exc())
                    if obj is not None:
                        obj.info = info #TODO: set ptype on base Token, change to info
                        line += match.group(0).count('\n')
                        pos = match.end()
                        break
                    else:
                        continue

            if match is None:
                #print pattern
                #print '---------------------'
                #print repr(text[pos:])
                #print 'Stoped at line ', info.line
                break
        #if pos < n: #TODO: better exception
        #    print repr(text[pos:])

    def buildObject(self, parent, info):
        obj = info.pattern.function(info, parent)
        return obj

class RecursiveLexer(Lexer):
    def __init__(self, base, *args):
        Lexer.__init__(self)
        self._grammers = collections.OrderedDict()
        self._grammers[base] = Grammer()
        for name in args:
            self._grammers[name] = Grammer()

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
            if key in info.keys():
                text = info[key]
                if text is not None:
                    self.tokenize(obj, grammer, text, info.line)
        return obj
