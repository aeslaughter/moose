import collections
import logging

import moosedown
from moosedown import tree
from Grammer import Grammer

LOG = logging.getLogger(__name__)
class Lexer(object):

    def tokenize(self, text, parent, grammer, line=1):

        if isinstance(text, moosedown.tree.page.PageNodeBase):
            self._node = text
            text = self._node.content

        n = len(text)
        pos = 0
        mo, pattern = self._search(text, grammer, pos)
        while (mo is not None) and (pos < n): # pos < n is needed to avoid empty string
            obj = self.buildObject(pattern, mo, parent, line)
            line += mo.group(0).count('\n')
            pos = mo.end()
            mo, pattern = self._search(text, grammer, pos)

        if pos < n:
            obj = tree.tokens.Unknown(content=text[pos:])
            obj.parent = parent
            obj.line = line

    def _search(self, text, grammer, position=0):
        for pattern in grammer:
            m = pattern.regex.match(text, position)
            if m:
                return m, pattern
        return None, None

    def buildObject(self, pattern, match, parent, line):
        try:
            obj = pattern.function(match, parent)
        except Exception as e:
            if self._node and self._node.source:
                msg = "\nAn exception occured while tokenizing, the exception was raised when\n" \
                      "executing the {} object while processing the following content.\n" \
                      "{}:{}".format(pattern.name, self._node.source, line)
            else:
                msg = "\nAn exception occured on line {} while tokenizing, the exception was\n" \
                      "raised when executing the {} object while processing the following content.\n"
                msg = msg.format(line, pattern.name)

            LOG.exception(moosedown.common.box(match.group(0), title=msg, line=line))
            raise e

        obj.line = line
        obj.match = match
        if self._node and self._node.source:
            obj.source = self._node.source
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

    def grammers(self):
        return self._grammers

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
