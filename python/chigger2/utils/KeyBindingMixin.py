#pylint: disable=missing-docstring
#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import collections
import copy
import textwrap
import mooseutils

KeyBinding = collections.namedtuple('KeyBinding', 'key shift description function args')

class KeyBindings(object):
    """
    A container for storing keybindings.

    This container is needed to allow for a staticmethod at the class level for populating
    the available bindings. The static method is needed to allow for MooseDocs to extract
    the bindings without instantiating the object.
    """
    def __init__(self):
        self.bindings = collections.OrderedDict()

    def add(self, key, func, shift=False, desc=None, args=None):
        """
        Add a keybinding.
        """
        args = args or tuple()
        if (key, shift) not in self.bindings:
            self.bindings[(key, shift)] = set()
        self.bindings[(key, shift)].add(KeyBinding(key, shift, desc, func, args))

class KeyBindingMixin(object):
    """
    Class for inheriting key binding support for an object.
    """
    @staticmethod
    def validOptions():
        from . import Options
        opt = Options()
        opt.add('interactive', True, doc="Toggle indicating if the object is interactive.")
        return opt

    @staticmethod
    def validKeyBindings():
        return KeyBindings()

    def __init__(self):
        self.__keybindings = self.validKeyBindings()

    def keyBindings(self):
        return copy.copy(self.__keybindings.bindings)

    def getKeyBindings(self, key, shift=False):
        return self.__keybindings.bindings.get((key, shift), set())

    @staticmethod
    def printKeyBindings(bindings):
        """
        Helper for printing keybindings.
        """
        n = 0
        out = []
        for key, value in bindings.iteritems():
            tag = 'shift-{}'.format(key[0]) if key[1] else key[0]
            desc = [item.description for item in value]
            out.append([tag, '\n\n'.join(desc)])
            n = max(n, len(tag))

        for key, desc in out:
            key = mooseutils.colorText('{0: >{w}}: '.format(key, w=n), 'GREEN')
            print '\n'.join(textwrap.wrap(desc, 100, initial_indent=key,
                                          subsequent_indent=' '*(n + 2)))


    def interactive(self):
        """
        Return the interactive state for the object.
        """
        return self.getOption('interactive')
