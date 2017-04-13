# MediaExtension

The media extension provides markdown commands for adding images, slideshow, and videos.

## Images

!image docs/media/memory_logger-plot_multi.png width=30% padding-left=20px float=right caption=The [memory_logger](/memory_logger.md) is a utility that allows the user to track the memory use of a simulation.

It is possible to include images with more flexibility than standard markdown.

The markdown keyword for MOOSE images is `!image` followed by the filename as shown below. This
command, like most of the other special MOOSE markdown commands except arbitrary html attributes
that are then applied to the "style" attribute. For example, the following syntax was used to
include the image on the right.

```markdown
!image docs/media/memory_logger-plot_multi.png width=30% padding-left=20px float=right caption=The [memory_logger](/memory_logger.md) is a utility that allows the user to track the memory use of a simulation.
```

!extension-settings moose_image title=Command Settings (`!image`)

## Videos

Locally stored or hosted videos can be displayed using the `!video` syntax. This works in the same
fashion as the `!image` command, but also includes some extra settings as listed in the table
below.

!video http://clips.vorwaerts-gmbh.de/VfE.webm width=100%

!extension-settings moose_video title=Command Settings (`!video`)


## Slideshows
A sequence of images can be shown via a `slider`.
By default the images will auto cycle between images.

A simple example:

```markdown
!slider
    intro.png
    other*.png
```

This would create a slideshow with the first image as `intro.png` and the next images those that are matched by the wildcard `other*.png`.

Valid options for the slider are standard CSS options (see example below).  Changing
the interval between slides, transition time, and button layout is not possible
at this time.

CSS options for background images can be applied to individual images as keyword
pairs.  Additionally, captions can be added to each image and
modified with appropriate CSS options.

Any option that appears after the image (but before "caption", if it exists)
will be applied to the image.  Any option that
appears after "caption" will be applied to the caption.

A full slideshow example might be:
```markdown
!slider max-width=50% left=220px
    docs/media/memory_logger-darkmode.png caption= Output of memory logging tool position=relative left=150px top=-150px
    docs/media/testImage_tallNarrow.png background-color=#F8F8FF caption= This is a tall, thin image color=red font-size=200% width=200px height=100%
    docs/media/github*.png background-color=gray
    docs/media/memory_logger-plot_multi.png
```

!slider max-width=50% left=220px
    docs/media/memory_logger-darkmode.png caption= Output of memory logging tool position=relative left=150px top=-150px
    docs/media/testImage_tallNarrow.png background-color=#F8F8FF caption= This is a tall, thin image color=red font-size=200% width=200px height=100%
    docs/media/github*.png background-color=gray
    docs/media/memory_logger-plot_multi.png

!extension-settings moose_slider title=Command Settings (`!slider`)


!extension MediaExtension title=MediaExtension Configuration Options
