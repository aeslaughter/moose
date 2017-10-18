import collections

import moosedown
from moosedown import tree
from Grammer import Grammer

class Lexer(object):

    def tokenize(self, text, parent, grammer, line=1):
        n = len(text)
        pos = 0
        mo, pattern = self._search(text, grammer, pos)
        while (mo is not None) and (pos < n): # pos < n is needed to avoid empty string
            line += mo.group(0).count('\n')
            obj = self.buildObject(pattern, mo, parent, line)
            pos = mo.end()
            mo, pattern = self._search(text, grammer, pos)

        if pos < n:
            obj = tokens.Unknown(content=text[pos:])
            obj.parent = parent
            obj.line = line

    def _search(self, text, grammer, position=0):
        for pattern in grammer:
            m = pattern.regex.match(text, position)
            if m:
                return m, pattern
        return None, None

    def buildObject(self, pattern, match, parent, line):
        obj = pattern.function(match, parent, line)
        obj.line = line
        return obj


class RecursiveLexer(Lexer):
    def __init__(self, base, *args):
        super(RecursiveLexer, self).__init__()
        self._grammers = collections.OrderedDict()
        self._grammers[base] = Grammer()
        for name in args:
            self._grammers[name] = Grammer()

    def tokenize(self, text, parent, grammer=None, line=1):
        if grammer is None:
            grammer = self._grammers[self._grammers.keys()[0]]
        super(RecursiveLexer, self).tokenize(text, parent, grammer, line)

    def grammer(self, group=None):
        if group is None:
            group = self._grammers.keys()[0]
        return self._grammers[group]

    def add(self, group, *args):
        self.grammer(group).add(*args)

    def buildObject(self, pattern, match, parent, line):
        obj = super(RecursiveLexer, self).buildObject(pattern, match, parent, line)
        for key, value in self._grammers.iteritems():
            if key in match.groupdict():
                text = match.group(key)
                if text is not None:
                    self.tokenize(text, obj, value, line)
        return obj
