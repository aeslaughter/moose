# Listing Extension

The listing extension provides a mechanism for creating source code listings. The system allows
for the inclusion of complete or partial snippets of the desired source code and includes
the ability to parse MOOSE input files and separate out blocks. The main purpose is to avoid
copying code or input syntax into the documentation to avoid out-of-date content.

The extension provides the `!listing` command, which allows for numbered captions to be
applied, the [floats.md] provides additional details. The following table list the avaible
configure options for the extension.

!devel settings module=moosedown.extensions.listing object=ListingExtension

The `!listing` command has the capability to include text from arbitrary files, such as source code
files. There is a wide range of settings that are available to specialize how the code is imported.
The complete list of available of settings are provided in [moose-listing] and the sections
below provide various examples of using some of these settings.

!devel settings module=moosedown.extensions.listing
                object=GeneralListingCommand
                id=moose-listing
                caption=Settings available when capturing text from a file with the `listing` command.

## Complete Files

You can include complete files from the repository. For example, the
following creates the code listing in [example-listing-complete].

!devel! example id=example-listing-complete caption=Example for showing a complete file.
!listing framework/src/kernels/Diffusion.C
!devel-end!

## Single Line Match

It is possible to show a single line of a file by including a snippet that allows the line to be
located within the file. If multiple matches occur only the first match will be shown. For example,
the call to `addClassDescription` can be shown by adding the following.

!devel! example id=example-listing-line caption=Example for displaying a single line from a file.
!listing framework/src/kernels/Diffusion.C line=computeQp
!devel-end!


### Range Line match

Code starting and ending on lines containing a string is also possible by using the 'start' and
'end' options. If 'start' is omitted then the snippet will start at the beginning of the file.
Similarly, if 'end' is omitted the snippet will include the remainder of the file content.

!devel! example id=example-listing-start-end caption=Example listing using the "start" and "end" settings.
!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=Kernels end=Executioner
!devel-end!

## Input File Block
Like for C++ files, [MOOSE] input files also have additional capability, mainly the "block" setting (see \ref{moose-input-listing} for a complete list). Including the block name the included content will be limited to the content matching the supplied name. Notice that the supplied name may be approximate; however, if it is not unique only the first match will appear.

```markdown
!listing test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=input caption=Code listing of [MOOSE] input file block.
```

!listing test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=input caption=Code listing of [MOOSE] input file block.

!extension-settings moose-input-listing caption=List of available settings when including [MOOSE] input (*.i) files.

## Fenced Code Blocks

The `!listing` command can also be utilized to wrap inline fenced code blocks, by placing the command on the line before the fenced code as shown in \ref{fenced}.

!listing id=fenced caption=Example markdown of a fenced code block with the listing command.
~~~markdown
!listing id=combo caption=That's amazing! I've got the same combination on my luggage!
```c++
int combo = 12345;
```
~~~

The available settings for the `!listing` command is reduced from the versions that include files,
because a majority of the options to apply. The complete list is provided in \ref{moose_fenced_code_block}.

!extension-settings moose_fenced_code_block caption=List of available settings when including using the `listing` command with fenced code blocks.

## Extension Configuration
The configuration options for ListingExtension extension are include in \ref{ListingExtension}.

!extension ListingExtension

[MOOSE]: www.mooseframework.org
