import collections
import logging

import moosedown
from moosedown import tree, common
from Grammer import Grammer

LOG = logging.getLogger(__name__)
class Lexer(object):
    def __init__(self):
        self._node = None

    def tokenize(self, text, parent, grammer, line=1):

        #TODO: "text" should be required to be a node and self._node should be removed
        if isinstance(text, moosedown.tree.page.PageNodeBase):
            self._node = text
            text = self._node.content

        n = len(text)
        pos = 0
        mo, pattern = self._search(text, grammer, pos)
        while (mo is not None) and (pos < n): # pos < n is needed to avoid empty string

            #TODO: move exception handling to here (except common.TokenizeException)
            try:
                obj = self.buildObject(pattern, mo, parent, line)
            except common.TokenizeException as e:
                self._errorHandler(e, mo, pattern, self._node, line)
                obj = tree.tokens.Error(match=mo)

            line += mo.group(0).count('\n')
            pos = mo.end()
            mo, pattern = self._search(text, grammer, pos)

        #if pos < n:
        #    obj = tree.tokens.Unknown(content=text[pos:])
        #    obj.parent = parent
        #    obj.line = line

    def _search(self, text, grammer, position=0):
        for pattern in grammer:
            m = pattern.regex.match(text, position)
            if m:
                return m, pattern
        return None, None

    def buildObject(self, pattern, match, parent, line):
        obj = pattern.function(match, parent)


        #TODO: test obj is correct type

        #TODO: line and match should not be needed, all components should raise a TokenExceptions
        #obj.line = line #
        #obj.match = match

        # TODO: This should be handled at RecursiveLexer level
        if self._node and self._node.source:
            obj.source = self._node.source

        return obj

    @staticmethod
    def _errorHandler(exception, match, pattern, node, line):
        if isinstance(node, tree.page.LocationNodeBase):
            msg = "\nAn exception occurred while tokenizing, the exception was raised when\n" \
                  "executing the {} object while processing the following content.\n" \
                  "{}:{}".format(pattern.name, node.source, line)
        else:
            msg = "\nAn exception occurred on line {} while tokenizing, the exception was\n" \
                  "raised when executing the {} object while processing the following content.\n"
            msg = msg.format(line, pattern.name)

        LOG.exception(moosedown.common.box(match.group(0), title=msg, line=line))

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
