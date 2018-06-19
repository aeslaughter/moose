# Chigger

The "chigger" python library is framework for creating visualizations via scripts. The
package was created as a "mite to replace [EnSight](https://www.ensight.com/)." This package
is the basis of the Peacock result tab.

The chigger package is currently under heavy development to make the tools more interactive, via the
command-line, to create visualization scripts rapidly. So, please be patient as these changes take
shape as does the associated documentation.

If you are interested in using chigger, please refer to the tests (`moose/python/chigger/tests`)
until the documentation is complete.

## Simple Example

!listing simple/simple.py start=import


## Interaction

When a window is created, in an interactive mode, it is possible to manipulate the objects
contained in the window using keybindings. There are two sets of keybindings: general keybindings
that apply to all objects as shown in [general-keybindings] as well as bindings that are specific
to each result object.

!chigger keybindings object=chigger.observers.MainWindowObserver
                     id=general-keybindings
                     caption=General keybindings available interactive windows.
