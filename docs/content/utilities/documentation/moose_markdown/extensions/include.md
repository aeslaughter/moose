# IncludeExtension

The main driver behind developing the MooseDocs documentation system was to create a single source
for all locations and allow for the same piece of text to be reused in multiple locations. Therefore, it is possible to include markdown within markdown using the `!include` command.

For example, \ref{include-demo}

`!listing id=include-demo`

!include docs/content/utilities/documentation/moose_markdown/extensions/global.md re=The\sglobal.*?applied\.
