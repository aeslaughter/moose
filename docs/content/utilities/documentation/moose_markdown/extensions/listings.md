# Listings Extension

It is possible to include complete or partial C++ or input files from the local MOOSE repository.
The `!listing` command allows for numbered captions to be applied, the [Numbered Floats](extensions/numbered_floats.md) provides additional details.

## Complete Files
You can include complete files from the repository. For example, the
following creates the code listing in \ref{complete}.

```markdown
!listing framework/src/kernels/Diffusion.C id=complete caption=Code listing showing a complete file. style=max-height:250px;overflow-y:scroll
```

!listing framework/src/kernels/Diffusion.C id=complete caption=Code listing showing a complete file. style=max-height:250px;overflow-y:scroll

## Single Line Match
It is possible to show a single line of a file by including a snippet that allows the line to be
located within the file. If multiple matches occur only the first match will be shown. For example,
the call to `addClassDescription` can be shown by adding the following.

```markdown
!listing framework/src/kernels/Diffusion.C id=line caption=Code listing for a single line of a file. line=addClassDescription
```

!listing framework/src/kernels/Diffusion.C id=line caption=Code listing for a single line of a file. line=addClassDescription

## Range Line match
Code starting and ending on lines containing a string is also possible by using the 'start' and
'end' options. If 'start' is omitted then the snippet will start at the beginning of the file.
Similarly, if 'end' is omitted the snippet will include the remainder of the file content.

```markdown
!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=Kernels end=Executioner overflow-y=scroll max-height=500px id=range caption=Code block including lines within a range.
```

!listing test/tests/kernels/simple_diffusion/simple_diffusion.i start=Kernels end=Executioner overflow-y=scroll max-height=500px id=range caption=Code block including lines within a range.

## Class Methods
By including a method name, in C++ syntax fashion, it is possible to include specific methods from
C++ classes in MOOSE. For example, the following limits the included code to the `computeQpResidual`
method.

```markdown
!listing framework/src/kernels/Diffusion.C method=computeQpResidual id=clang caption=Code listing using the clang parser.
```

<!--
!listing framework/src/kernels/Diffusion.C method=computeQpResidual id=clang caption=Code listing using the clang parser.
-->

!!! warning "Warning"
    This method uses the clang parser directly, which can be slow. Thus, in general source code should be
    included using the line and range match methods above and this method reserved for cases where those methods
    fail to capture the necessary code.


## Input File Block
By including a block name the included content will be limited to the content matching the supplied name. Notice that the supplied name may be approximate; however, if it is not unique only the first match will appear.

```markdown
!listing test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=input caption=Code listing of [MOOSE] input file block.
```

!listing test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels id=input caption=Code listing of [MOOSE] input file block.

## Fenced Code Blocks

The `!listing` command can also be utilized to wrap inline fenced code blocks, by placing the command on the line before the fenced code as shown in \ref{fenced}.

!listing id=fenced caption=Example markdown of a fenced code block with the listing command.
~~~
!listing id=combo caption=That's amazing! I've got the same combination on my luggage!
```c++
int combo = 12345;
```
~~~


## Extension Configuration


## Extension Command Settings
