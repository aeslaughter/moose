# FloatExtension

The FloatExtension provides the ability to create numbered figures, table, and code listings that
can be referenced with the latex style `\ref{}` command. This extension works in union with
the [media](extensions/media.md) and [include](extensions/include.md). When this extension is
included, adding the "id" attribute to the following commands will automatically convert to command
to include a numbered caption that can be referenced.

* Listings: `!text`, `!input`, `!clang`
* Figures: `!image`, `!video`

Additionally, this extension adds the `!table` command as detailed in [Tables](#tables) section.

## Figures

When writing documentation it is customary to reference figures within text by number. To create a numbered figure use
the `!image` or `!video` markdown syntax, but include an "id" options with the label desired for referencing. For example: `!image path/to/demo.png caption=The Caption id=fig:demo`

!image docs/media/memory_logger-plot_multi.png width=300px float=right padding-left=20px caption=The numbered prefix is automatically applied to the caption. id=fig:demo

The caption will automatically be prefixed with the figure number (e.g., Figure \ref{fig:demo}). The
numbering begins at one and is reset on each page.

Figures can be referenced with latex style reference commands. For example, using `\ref{fig:demo}` results in a
reference to Figure \ref{fig:demo}. If an invalid "id" is supplied the reference will displayed in red: \ref{fig:invalid_id}.



<!--
!video http://clips.vorwaerts-gmbh.de/VfE.webm video-width=1500px padding-right=10px float=left id=big_buck_bunny caption=Big Buck Bunny is an open-source animated short.
-->


## Tables

!table id=table:testing caption=This is an example table with a caption.
| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|----|
| 2 | 4 | 6 | 8 | 10 |

Similar to figures, tables can be referenced: Table \ref{table:testing}.

## Listings

!text framework/src/kernels/Diffusion.C id=diffusion caption=Diffusion Kernel
