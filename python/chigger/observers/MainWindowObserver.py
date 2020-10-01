#* This file is part of the MOOSE framework
#* https://www.mooseframework.org
#*
#* All rights reserved, see COPYRIGHT for full restrictions
#* https://github.com/idaholab/moose/blob/master/COPYRIGHT
#*
#* Licensed under LGPL 2.1, please see LICENSE for details
#* https://www.gnu.org/licenses/lgpl-2.1.html
import re
import copy
import vtk

import mooseutils
from .ChiggerObserver import ChiggerObserver
from .. import utils
from .. import geometric

class MainWindowObserver(ChiggerObserver, utils.KeyBindingMixin):
    """
    The main means for interaction with the chigger interactive window.
    """
    RE = re.compile(r"(?P<key>[^\s=]+)=(?P<value>.*?)(?=(?:,\s[^\s=]+=|\Z)|\)\Z)")

    @staticmethod
    def validOptions():
        opt = ChiggerObserver.validOptions()
        opt += utils.KeyBindingMixin.validOptions()
        return opt

    @staticmethod
    def validKeyBindings():
        bindings = utils.KeyBindingMixin.validKeyBindings()

        bindings.add('v', MainWindowObserver.nextViewport, desc="Select the next viewport.")
        bindings.add('v', MainWindowObserver.nextViewport, shift=True, args=(True,),
                     desc="Select the previous viewport.")

        bindings.add('s', MainWindowObserver.nextSource,
                     desc="Select the next source in the current viewport.")
        bindings.add('s', MainWindowObserver.nextSource, shift=True, args=(True,),
                     desc="Select the previous source in the current viewport.")

        bindings.add('p', MainWindowObserver._onPrintOptions,
                     desc="Display the available key, value options for the active source or viewport.")
        bindings.add('p', MainWindowObserver._onPrintSetOptions, shift=True,
                     desc="Display the available key, value options as a 'setOptions' method call for the active source of viewport.")

        bindings.add('t', MainWindowObserver.deactivate, desc="Clear selection(s).")

        # TODO:
        # bindinds.add('q',...)


        # TODO: This still needs some work, hitting enter doesn't seem to exit correctly
        #bindings.add('o', MainWindowObserver._onChangeOption,
        #             desc="Prompt the user to change an option via the command-line.")

        # TODO: This needs some work also, it can mess up spacing and and the 'opacity' from the
        #       Text annotation does not show up
        #bindings.add('w', MainWindowObserver._onWriteChanges,
        #             desc="Write the changed settings for an active object to the script file.")

        return bindings

    def __init__(self, *args, **kwargs):
        ChiggerObserver.__init__(self, *args, **kwargs)
        utils.KeyBindingMixin.__init__(self)

        self.addObserver(vtk.vtkCommand.KeyPressEvent, self._onKeyPressEvent)

        # Disable interaction by default, but honor user specified interaction
        for viewport in self.getViewports():
            v_i = viewport.getOption('interactive') if viewport._options.isSetByUser('interactive') else False
            v_h = viewport.getOption('highlight') if viewport._options.isSetByUser('highlight') else v_i
            viewport.setOptions(highlight=v_h, interactive=v_i)

            for source in viewport.sources():
                s_i = source.getOption('interactive') if source._options.isSetByUser('interactive') else False
                s_h = source.getOption('highlight') if source._options.isSetByUser('highlight') else s_i
                source.setOptions(highlight=s_h, interactive=s_i)

    def getViewports(self):
        """Complete list of available Viewport objects"""
        return [viewport for viewport in self._window.viewports() if viewport.getOption('layer') > 0]

    def getActiveViewport(self):
        """Current active (highlighted) Viewport object"""
        for viewport in self.getViewports():
            if viewport.getOption('interactive'):
                return viewport
        return None

    def setActiveViewport(self, viewport):
        """Activate the supplied viewport and disable all others"""
        for vp in self.getViewports():
            active = viewport is vp
            vp.setOptions(interactive=active, highlight=active)
            vp.updateInformation()

    def nextViewport(self, decrease=False):
        """Activate the "next" viewport object."""
        self.debug('Select Next Viewport')

        # Remove highlighting from the active source.
        self.setActiveSource(None)

        # Determine the index of the Viewport to be set to active
        index = 0
        viewports = self.getViewports()
        current = self.getActiveViewport()
        if current is not None:
            index = viewports.index(current)
            index = index - 1 if decrease else index + 1

        current = viewports[index] if index < len(viewports) else None
        self.setActiveViewport(current)

        self._window.render()

    def getSources(self):
        """Complete list of available ChiggerSourceBase objects"""
        return [source for viewport in self.getViewports() for source in viewport.sources() if source.getOption('pickable')]

    def getActiveSource(self):
        """Current active ChiggerSourceBase object"""
        for source in self.getSources():
            if source.getOption('interactive'):
                return source
        return None

    def setActiveSource(self, source):
        for s in self.getSources():
            active = s is source
            s.setOptions(highlight=active, interactive=active)
            s._viewport.updateInformation()
            s.updateInformation()

    def nextSource(self, decrease=False):
        """
        Activate the "next" source object
        """
        self.debug('Select Next Source')

        # Remove active viewport
        self.setActiveViewport(None)

        # Determine the index of the ChiggerSourceBase to be set to active
        sources = self.getSources()
        current = self.getActiveSource()
        index = 0
        if current is not None:
            index = sources.index(current)
            index = index - 1 if decrease else index + 1

        current = sources[index] if index < len(sources) else None
        self.setActiveSource(current)

        self._window.render()

    def deactivate(self):
        """Remove all interaction seclections"""
        self.setActiveViewport(None)
        self.setActiveSource(None)

    def writeChanges(self, obj):
        """Write changes from the supplied object directly to the script, if desired"""

        # Extract the option information
        trace = obj._init_traceback[0]
        filename = trace[0]
        line = trace[1]

        # Inline function for swapping options
        output, sub_output = obj._options.getNonDefaultOptions()
        def sub_func(match):
            key = match.group('key')
            value = match.group('value')
            if key in output:
                return '{}={}'.format(key, repr(obj.getOption(key)))
            return match.group(0)

        # Read the original file
        with open(filename, 'r') as fid:
            lines = fid.readlines()

        # Swap line with new option(s)
        content = self.RE.sub(sub_func, trace[3])
        new_lines = copy.copy(lines)
        new_lines[line-1] = '{}\n'.format(content)

        # Create and show the diff, if it exists
        diff = mooseutils.text_unidiff('\n'.join(new_lines), '\n'.join(lines), out_fname=filename, gold_fname=filename, num_lines=1)
        if not diff:
            self.info("No changes to the filename {} to write.", filename)
            return

        # Show the proposed changes
        n = max(max([len(l) for l in lines]), max([len(l) for l in new_lines]))
        print('='*n)
        print('{} PROPOSED CHANGES'.format(filename))
        print('='*n)
        print(diff.strip('\n'))

        # Prompt the user for an action
        choice = self._prompt("Would you like to overwrite[w], create a diff[d], or quit[q]? ")

        if choice == 'd':
            with open(filename + '.diff', 'w') as fid:
                fid.write(diff)
        elif choice == 'w':
            with open(filename, 'w') as fid:
                fid.write(''.join(new_lines))

    def _prompt(self, msg):
        self._window.getVTKInteractor().Disable()
        choice = input(msg)
        self._window.getVTKInteractor().Enable()
        return choice

    def _onKeyPressEvent(self, obj, event):
        """
        The function to be called by the vtkInteractor KeyPressEvent (see init).

        Inputs:
            obj, event: Required by VTK.
        """
        key = obj.GetKeySym().lower()
        shift = obj.GetShiftKey()
        self.debug('Key press: {}, shift={}', key, shift)

        # This objects bindings
        for binding in self.getKeyBindings(key, shift):
            binding.function(self, *binding.args)

        # Viewport options
        viewport = self.getActiveViewport()
        if viewport is not None:
            for binding in viewport.getKeyBindings(key, shift):
                binding.function(viewport, *binding.args)

        # Source options
        source = self.getActiveSource()
        if source is not None:
            for binding in source.getKeyBindings(key, shift):
                binding.function(source, *binding.args)

        self._window.render()

    def _onWriteChanges(self):


        # Determine the object to glean options from and error if two things are active
        source = self.getActiveSource()
        viewport = self.getActiveViewport()
        if (source is not None) and (viewport is not None):
            self.error("Both a source and viewport are active which is not supported for writing, because of potential output conflicts.")
            return
        elif (source is None) and (viewport is None):
            self.warning("No active source of viewport to inspect for option changes, so there is nothing to write.")
            return

        obj = source or viewport
        self.writeChanges(obj)

    def _onPrintOptions(self):
        """Print a list of all available options for active objects."""
        def printHelper(obj):
            if obj is not None:
                print(mooseutils.colorText('\n{} Available Options:'.format(obj.name()), 'LIGHT_CYAN'))
                print(obj._options)

        printHelper(self.getActiveViewport())
        printHelper(self.getActiveSource())

    def _onPrintSetOptions(self, *args):
        """Print python code for the 'setOptions' method for active objects"""
        def printHelper(obj):
            if obj is not None:
                output, sub_output = obj._options.toScript()
                print('\n{} -> setOptions({})'.format(obj.name(), ', '.join(output)))
                for key, value in sub_output.items():
                    print('{} -> setOptions({}, {})'.format(obj.name(), key, ', '.join(repr(value))))

        printHelper(self.getActiveViewport())
        printHelper(self.getActiveSource())


    def _onChangeOption(self):
        """Prompt user on command line to change a parameter by name"""

        # Determine the object to glean options from and error if two things are active
        source = self.getActiveSource()
        viewport = self.getActiveViewport()
        if (source is not None) and (viewport is not None):
            self.error("Both a source and viewport are active which is not supported for writing, because of potential output conflicts.")
            return
        elif (source is None) and (viewport is None):
            self.warning("No active source of viewport to inspect for option changes, so there is nothing to write.")
            return

        obj = source or viewport

        # Get the name of the parameter to change
        while True:
            param = self._prompt('Enter the option to change (press enter to abort): ')
            if len(param) > 0 and (param not in obj._options):
                msg ="'{}' is not an option in {} object, available options include:\n  ".format(param, obj.name())
                msg += '\n  '.join(obj._options.keys())
                print(msg)
                continue
            break

        # Get the value of the parameter
        if len(param) > 0:
            print(obj._options.toString(param))
            value = self._prompt('Enter the value of the option to change: ')
            obj.setOption(param, eval(value))
