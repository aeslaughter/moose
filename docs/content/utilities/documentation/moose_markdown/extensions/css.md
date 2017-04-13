# CSS Options
To increase the flexibility of markdown content it is possible to inject [CSS](https://en.wikipedia.org/wiki/Cascading_Style_Sheets)
directly into sections of text using the `!css` command.

## In-line CSS

You can provide valid CSS attributes to any of the [MOOSE markdown extensions](moose_flavored_markdown/index.md#MooseDocs-extensions) markdown extensions (e.g., !text). In
general, it is possible to set "id" and "style" attributes via the options following the command.

```
!text test/tests/kernels/simple_diffusion/simple_diffusion.i id=diffusion style=float:right;padding-left:20px;width:300px
```

However, any setting that is not recognized (i.e., it is not in the settings listed with the command) are automatically
appended to the "style" settings. Therefore, the following is also valid.

```
!text test/tests/kernels/simple_diffusion/simple_diffusion.i id=diffusion float=right padding-left=20px width=300px
```

!input test/tests/kernels/simple_diffusion/simple_diffusion.i block=BCs float=right padding-left=20px font-size=smaller

As shown to the right, it is possible to utilize inline CSS to float portions of the document. Within the markdown
of this section the following command was placed directly before this paragraph.

```markdown
!input test/tests/kernels/simple_diffusion/simple_diffusion.i block=Kernels float=right padding-left=20px font-size=smaller
```

The extra CSS settings 'float's the content to the right, which should allow this section of text and elements, to appear to the left of the code block, and wrap around it.

  *  The float should work with lists.

!!! Info
    It should also work with admonitions.


## Block CSS Options
You can apply a style sheet to a markdown paragraph through the use of !css extension:

```markdown
!css font-size=smaller margin-left=70% color=red text-shadow=1px 1px 1px rgba(0,0,0,.4)
This paragraph should be of a smaller red font with a black offset text shadow. The text
will be aligned to the right due to the margin-left attribute (nice trick to preserve the
'justify' attribute currently in use)

An empty new line, designates the end of the css block.

!css font-size=smaller margin-left=70% color=red text-shadow=1px 1px 1px rgba(0,0,0,.4)
Another paragraph modified by CSS.
```

!css font-size=smaller margin-left=70% color=red text-shadow=1px 1px 1px rgba(0,0,0,.4)
This paragraph should be of a smaller red font with a black offset text shadow. The text
will be aligned to the right due to the margin-left attribute (nice trick to preserve the
'justify' attribute currently in use)

An empty new line, designates the end of the css block.

!css font-size=smaller margin-left=70% color=red text-shadow=1px 1px 1px rgba(0,0,0,.4)
Another paragraph modified by CSS.

!extension-settings moose_css title=!css Command Settings
