# MOOSE Markdown Specification (MooseDown)
The following document details the MOOSE flavored [markdown] used for documenting MOOSE and
MOOSE-based applications with the MooseDocs system.

## Motivation
[markdown] is ubiquitous as a short-hand [HTML] format, especially among software developers.
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

## Design
The MooseDocs system, in particular, the MooseDown parsing is designed to be extendable. Thus,
all components, including the core language, is created as an extension.

## Settings
The MooseDown language adds key, value pairs to control the resulting rendered content. The use of
these pairs is uniform through out the specification and is integral to the flexibility of the
MooseDocs system. For example, the "style" keyword is used when rendering to [HTML] and allows the
`<h2>` style attribute to be set from the MooseDown file.

```language=markdown
## Heading Level Two style=font-size:2em
```

!alert note
The key, value pairs must be separated by an equal sign and cannot contain spaces on either side
of the equal. However, spaces within the value are allowed.

## Core Extension
The core extension is the portion of the MooseDown language that is designed to mimic [markdown]
syntax. As mentioned above MooseDown is far more strict than traditional [markdown] implementations.
For that reason there are many aspects of [markdown] that are not supported by MooseDown, the
following list illustrates some the "missing" [markdown] features. And, the following sections
detail the supported syntax.

- Underline style headings are not supported (i.e., `=====` and `-----`), see [Headings](#headings).
- Four space code indenting is not supported, see [Code](#code).


### Headings
!devel compare style=font-size:75%;padding-left:10pt;float:right;width:50%
~~~MooseDown language=markdown
# Level One
## Level Two
### Level Three style=font-size;14pt; id=level-three
#### Level Four
##### Level Five
###### Level Six
~~~HTML language=html
<h1>Level One</h1>
<h2>Level Two</h2>
<h3 style="font-size:14pt" id="level-three">Level Three</h3>
<h4>Level Four</h4>
<h5>Level Five</h5>
<h6>Level Six</h6>
~~~LaTeX language=latex
\part{Level One}
\chapter{Level Two}
\section{Level Three\label{level-three}}
\subsection{Level Four}
\subsubsection{Level Five}
\paragraph{Level Six}

All headings from level 1 to 6 must be specified using the hash (`#`) character, where the
number of hashes indicate the heading level. The hash(es) must be followed by a single space.

Following the heading [settings](#settings) may be applied. The available settings are detailed
in the table below.

!devel settings moosedown-headings

### Lists
#### Unordered List

- List items in MooseDown must begin with a dash (`-`), the asterisk is +not+ supported.
- List items may contain lists, code, or any other markdown item and the item content may
  span many lines.

  List items are continued by indenting the content to be included within the item by two spaces,
  which is how this paragraph was created.

- As mentioned above, lists can contain lists, which can contain lists, etc.

  - This sub-list is created by indenting the start of the list, again using a dash (`-`), by
    two spaces.

    Lists can be arbitrarily nested.

    - This is yet another nested list.
    - This list contains two items.

- A list will continue to add items until a line (at the current indent level for nested items)
  starts with any character except the dash (`-`).

For example, this paragraph halted the list. Therefore, any additional list items placed
after this paragraph will create a new list.

- This will begin a new list item.

- To create a new list immediately following another list, the two lists must be separated by
  two empty lines.


- This is a second list that was created as a separate list from what is above by placing two
  blank lines between list items.

!devel moosedown
- Item 1
- Item 2
~~~
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>

### Numbered List
1. A numbered list that starts with the number provided.

   This list is also nested because it doesn't start with two empty lines.

### Text Formatting

em, strong, need to add strikethrough, underline, subscript, superscript, mark, inserted

This is ***something* with various
levels** of html formatting *that
spans* many lines. It all *should* work
fine.

### Quotes

> This should be a block
of text that goes in a blockquote
tag.

It can contain multiple paragraphs but,
stops with two empty lines.

This is more.
> This should be another.


[AST]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[HTML]: https://en.wikipedia.org/wiki/HTML
[CommonMark]: http://commonmark.org/
[markdown]: https://en.wikipedia.org/wiki/Markdown
