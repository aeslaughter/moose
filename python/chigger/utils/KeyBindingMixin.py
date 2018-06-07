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

KeyBinding = collections.namedtuple('KeyBinding', 'key shift description function')

class KeyBindingMixin(object):
    def __init__(self):
        super(KeyBindingMixin, self).__init__()
        self.__keybindings = collections.OrderedDict()

    def keyBindings(self):
        return self.__keybindings

    def addKeyBinding(self, key, func, shift=False, desc=None):
        if (key, shift) not in self.__keybindings:
            self.__keybindings[(key, shift)] = set()
        self.__keybindings[(key, shift)].add(KeyBinding(key, shift, desc, func))

    def getKeyBindings(self, key, shift=False):
        return self.__keybindings.get((key, shift), [])
