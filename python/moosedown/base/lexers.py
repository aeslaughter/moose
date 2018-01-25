"""
Module for defining the default Lexer objects that plugin to base.Reader objects.
"""
import collections
import logging
import traceback

import moosedown
from moosedown import tree, common
from Grammer import Grammer

LOG = logging.getLogger(__name__)

class Grammer(object):
    """
    Defines a generic Grammer that contains the Token objects necessary to build an
    abstract syntax tree (AST). This class defines the order that the tokens will be
    applied to the Lexer object and the associated regular expression that define the
    text associated with the Token object.
    """

    #: Container for information required for creating a Token object.
    Pattern = collections.namedtuple('Pattern', 'name regex function')

    def __init__(self):
        self.__patterns = common.Storage(Grammer.Pattern)

    def add(self, name, regex, function, location=-1):
        """
        Method for adding a Token definition to the Grammer object.

        Inputs:
            name[str]: The name of the grammer definition, this is utilized for
                       ordering of the definitions.
            regex[re]: A compiled re object that defines what text the token should
                       be associated.
            function[function]: A function that accepts a regex match object as input and
                                returns a token object.
            location[int or str]:  (Optional) In the case of an int type, this is an
                                   index indicating the location in the list of definitions
                                   to insert. In the case of a str type the following syntax
                                   is support to insert definitions relative to other
                                   definitions.
                                        '_begin': Insert the new definition at the beginning
                                                  of the list of definitions, this is the same
                                                  as using an index of 0.
                                        '_end': Append the new definition at the end of the list
                                                of definitions (this is the default).
                                        '<foo': Insert the new definition before the definition
                                                named 'foo'.
                                        '>foo': Insert the new definition after the definition
                                                named 'foo'.
        """
        self.__patterns.add(name,
                            Grammer.Pattern(name=name, regex=regex, function=function),
                            location)

    @property
    def patterns(self):
        return self.__patterns


    def __getitem__(self, key):
        """
        Return the pattern for a given key.
        """
        return self.__patterns[key]

    def __iter__(self):
        """
        """
        for obj in self.__patterns:
            yield obj


class LexerInformation(object):
    """
    Lexer meta data object to keep track of necessary information for strong error reporting.

    Inputs:
        match[re.Match]: The regex match object from which a Token object is to be created.
        pattern[Grammer.Pattern]: Grammer pattern definition, see Grammer.py.
        line[int]: Current line number in supplied parsed text.
    """
    def __init__(self, match=None, pattern=None, line=None):
        self.__match = match
        self.__pattern = pattern
        self.__line = line

    @property
    def line(self):
        """
        Return the line number for the regex match.
        """
        return self.__line

    @property
    def pattern(self):
        """
        Return the Grammer.Pattern for the regex match.
        """
        return self.__pattern

    def __getitem__(self, value):
        """
        Return the regex group by number or name.

        Inputs:
            value[int|str]: The regex group index or name.
        """
        return self.__match.group(value)

    def keys(self):
        """
        List of named regex groups.
        """
        return self.__match.groupdict().keys()

    def iteritems(self):
        """
        Iterate over the named groups.
        """
        for key, value in self.__match.groupdict().iteritems():
            yield key, value

    def __contains__(self, value):
        """
        Check if a named group exists in the regex match.
        """
        return value in self.__match.groupdict()

    def __str__(self):
        """
        Return a resonable string for debugging.
        """
        return 'line:{} match:{} pattern:{}'.format(self.__line, self.__match, self.__pattern)


class Lexer(object):
    def __init__(self):
        self._node = None

    def tokenize(self, parent, grammer, text, line=1):


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
