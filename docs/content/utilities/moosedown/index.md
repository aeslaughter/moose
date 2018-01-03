# MOOSE Markdown Specification (MooseDown)
The following details the MOOSE flavored [markdown] used for documenting MOOSE and
MOOSE-based applications with the MooseDocs system.

## Motivation id=motivation
As a short-hand [HTML] format, [markdown] is ubiquitous, especially among software developers.
However, no standard exists and the original implementation was incomplete. Currently, there are
myriad implementations---often deemed "flavors"---of Markdown. [CommonMark](http://commonmark.org/)
is a proposed standard. However, this specification is syntactically loose. For example, when
defining lists the spacing is can be misleading, see [Example 273](http://spec.commonmark.org/0.28/#example-273) and [Example 268](http://spec.commonmark.org/0.28/#example-268) shows that some poorly defined behavior still
exists and it is stated that the associated rule "should prevent most spurious list captures."

Additionally, most parsers of this
specification do not support custom extensions or adding them is difficulty, from a user
perspective, because the parsing strategy used is complex and context dependent.

Originally, MooseDocs used the [markdown](http://pythonhosted.org/Markdown/) python package, which
worked well in the general sense. However, as the MooseDocs system matured a few short-comings were
found. The main problems, with respect to MooseDocs, was the parsing speed, the lack of an [AST],
and the complexity of adding extensions (i.e., there are too many extension formats). The lack of an
[AST] limited the ability to convert the supplied markdown to other formats (e.g., LaTeX).

For these reasons, among others not mentioned here, yet another [markdown] flavor was born. MOOSE
flavored Markdown ("MooseDown"). The so called MooseDown language is designed to be strict with
respect to format as well as easily extendable so that MOOSE-based applications can customize the
system to meet their documentation needs. The strictness allows for a simple parsing strategy to be
used and promotes uniformity among the MooseDown files.

| Extension | Description |
| :- | :- |
| [core](core.md) | Basic markdown syntax such as code blocks, lists, and bold text. |
| [include](include.md) | Allows for markdown files to be included, in similar fashion to the Latex \include command. |










[AST]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[HTML]: https://en.wikipedia.org/wiki/HTML
[CommonMark]: http://commonmark.org/
[markdown]: https://en.wikipedia.org/wiki/Markdown
