!config!
Renderer/collapsible-sections=[None, 'open', 'open', None, None, None]
Renderer/breadcrumbs=True
!config-end!

# Core Extension
The core extension is the portion of the MooseDocs language that is designed to mimic [markdown]
syntax. MooseDown is far more strict than traditional [markdown] implementations.
Therefore, the following sections should be read in detail to understand the supported syntax,
especially if you are familiar with more general markdown formats.
Syntax is separated into two groups: [block](#core-block) and [inline](#core-inline). Block
content is made of items that make, as the name suggests, blocks of text. Blocks of
text include items such as code snippets, quotations, and paragraphs themselves. On the other hand,
inline items are those that are applicable to small portions of text (e.g., words). Bold and
italics are two examples of inline items.

!alert! note title=MooseDown is a restricted version of [markdown].
To unify the markdown content and to create a fast parser a limited set of
markdown is being used to define the MooseDocs language. The following sections
detail the syntax that comprise the syntax.
!alert-end!

## Block Content id=core-block

In general, most block level syntax accepts key-value pair settings. Where the settings
appear within the block level syntax varies and is detailed in each section below. However,
the settings are applied in a uniform manner. Foremost, the key and value are separated by an
equal (`=`) sign +without spaces+ surrounding. The value may contain spaces, with the space after
the equal sign being the exception.

If syntax has settings the key-value pairs, the default value (if any), and a short description
will be provided in a table. For example, [code-settings] lists the available settings
for the fenced code blocks discussed in the [fenced-code] section.

### Code id=fenced-code
Code blocks or snippets---as shown in [fenced-code-example]---are created by enclosing the code for
display in triple backticks (```), this is commonly referred to as fenced code blocks. Two
requirements exist for creating the code blocks:

1. the backticks must be proceeded by an empty line and
1. the backticks must start at the beginning of a line.

Settings for code blocks are defined by key-value pairings that follow the backticks;
[code-settings] lists the available settings for code blocks.

!devel! example caption=Basic fenced code block. id=fenced-code-example
```language=bash
export METHOD=opt
```
!devel-end!

!devel settings module=moosedown.extensions.core object=Code id=code-settings caption=Available settings for fenced code blocks.

### Quotations
Quote blocks are created by starting a line with the `>` character, with a single trailing
space.

!devel! example caption=Basic block quote.
> This is a quotation.
!devel-end!

Quote blocks can contain any valid markdown, including other quotations.

!devel! example caption=Nested content in block quotes.
> Foo
>
> > Another item, that also includes code.
> >
> > ```language=python
> > for i in range(10):
> >   print i
> > ```
> See, I told you.
!devel-end!

### Headings
All headings from level 1 to 6 must be specified using the hash (`#`) character, where the
number of hashes indicate the heading level. The hash(es) must be followed by a single space.

Settings may be applied after the heading title text, the available settings include the
following.

!devel settings module=moosedown.extensions.core object=HeadingHash

!devel! example caption=Basic use of all six heading levels.
# Level One
## Level Two
### Level Three
#### Level Four
##### Level Five
###### Level Six
!devel-end!


!devel! example caption=Use of settings within heading.
## Level Two style=font-size:15pt id=level-two
!devel-end!

### Unordered List id=unordered
Unordered list items in MooseDown +must+ begin with a dash (`-`).

!devel! example caption=Unordered list basic syntax.
- Item 1
- Item 2
!devel-end!

List items may contain lists, code, or any other markdown content and the item content may
span many lines. The continuation is specified by indenting the content to be included within the
item by two spaces.

!devel! example caption=Lists can contain other markdown content.
- Item with code
  Content can be contained within a list, all valid MooseDown syntax can be used.

  ```
  int combo = 12345;
  ```
- Another item
!devel-end!


As mentioned above, lists can contain lists, which can contain lists, etc.
A sub-list is created by indenting the start of the list, again using a dash (`-`), by two spaces.
The sub-list must also begin with a new line.

!devel! example caption=Nested unordered lists.
- A
- B

  - B.1
  - B.2

    - B.2.1
    - B.2.2
  -B.3
- C
!devel-end!

A list will continue to add items until a line (at the current indent level for nested items)
starts with any character except the dash (`-`).

To create a new list immediately following another list, the two lists must be separated by
two empty lines.

### Ordered List
A numbered list that starts with a numbered followed by a period and a single space. They work
in a similar fashion as [unordered lists](#unordered) and contain contain nested content. The
number used for the first item in the list will be the number used for the start of the list.

Again, to create another list following


!devel! example caption=Ordered lists with a starting number.
42. Foo
1. Bar


1. Another list that contains nested content.

   1. Ordered lists can be nested and contain markdown.

      ```
      code
      ```
!devel-end!

### Shortcuts
It is possible to define shortcuts for use within your document via a [shortcut link](#shortcut-link). The shortcuts
are defined using traditional markdown syntax.

!devel! example caption=Markdown shortcut definition.
[foo]: bar
!devel-end!



## Inline Content id=core-inline
### Text Formatting

em, strong, need to add strikethrough, underline, subscript, superscript, mark, inserted

This is ***something* with various
levels** of html formatting *that
spans* many lines. It all *should* work
fine.

### Shortcut links id=shortcut-link

[markdown]: https://en.wikipedia.org/wiki/Markdown
