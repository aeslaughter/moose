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

## Block Syntax id=core-block

Block level content, as the name suggest, are blocks of text. In all cases, blocks must
begin and end with empty lines (with the exception of the start and end of the file). This
restriction allows for special characters such as the hash (`#`) to be used at the start
of a line without conflicting with heading creation (see [headings]). Additionally, this
allows content and settings to be spanned across multiple lines.

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
display in triple back-ticks (```), this is commonly referred to as fenced code blocks. Two
requirements exist for creating the code blocks:

1. the back-ticks must be proceeded by an empty line and
1. the back-ticks must start at the beginning of a line.

Settings for code blocks are defined by key-value pairings that follow the back-ticks;
[code-settings] lists the available settings for code blocks.

!devel! example caption=Basic fenced code block. id=fenced-code-example
```language=bash
export METHOD=opt
```
!devel-end!

!devel settings module=moosedown.extensions.core object=Code id=code-settings caption=Available settings for fenced code blocks.

### Quotations

Quotation blocks are created by starting a line with the `>` character, with a single trailing
space as shown in [quote-example]. Then each additional line that belongs within the quotation
must also begin with a `>` character. Within the quotations any valid markdown is acceptable,
as shown in [quote-nested-example].

!devel! example caption=Basic block quote. id=quote-example
> This is a quotation.
!devel-end!

!devel! example caption=Nested content in block quotes. id=quote-nested-example
> Quotations begin with the `<` character and may
> contain any valid markdown content, include quotes and code as shown here.
>
> > This begins another quotation, which also contains a fenced code block.
> >
> > ```language=python
> > for i in range(10):
> >   print i
> > ```
>
> Since quotations are block content they must end with an empty line,
> therefore the nested quote above must contain an empty line.
!devel-end!

### Headings id=headings

Headings can range from level one to six and are specified using the hash (`#`) character, where the
number of hashes indicate the heading level (see [heading-basic-example]). The following is required
to define a heading:

1. the hash(es) must be followed by a single space,
1. the hash(es) must +not+ be proceeded by a space.


Settings, as listed in [heading-settings], are be applied after the heading title text and as shown in
[heading-multiline] headings may also span multiple lines.

!devel! example caption=Basic use of all six heading levels. id=heading-basic-example
# Level One

## Level Two

### Level Three

#### Level Four

##### Level Five

###### Level Six
!devel-end!

!devel! example caption=Use of settings within heading. id=heading-settings
## Level Two style=font-size:75pt;color:red; id=level-two
!devel-end!

!devel! example caption=Use of settings within heading. id=heading-multiline
## A Heading May Span
Multiple Lines (this is useful if they are really long)
   style=font-size:15pt
   id=level-two
!devel-end!

!devel settings module=moosedown.extensions.core object=HeadingHash caption=Available settings for headings. id=heading-settings

### Unordered List id=unordered

Unordered list items in MooseDown +must+ begin with a dash (`-`), as shown below in
[unordered-basic-example]. As with any block item, a list must be proceeded and followed by an empty
line. However, lists have additional behavior that allow for nested content to be included.

1. An empty line will not stop the list if the following line begins with another list marker
   (i.e., `-`), in this case the list continues.

1. An empty line followed by a non-list marker---everything except a hyphen---will stop the
   list. Otherwise, a list will stop if +two+ empty lines are encountered, otherwise it will
   continue to add items to the current list.

List items may contain lists, code, or any other markdown content and the item content may
span many lines. The continuation is specified by indenting the content to be included within the
item by two spaces, as shown in [unordered-nested-example].

!devel! example caption=Unordered list basic syntax. id=unordered-basic-example
- Item 1
- Item 2
!devel-end!


!devel! example caption=Lists can contain other markdown content. id=unordered-nested-example
- Item with code
  Content can be contained within a list, all valid MooseDown syntax can be used.

  ```
  int combo = 12345;
  ```

- Another item
!devel-end!


As mentioned above, lists can contain lists, which can contain lists, etc.
A sub-list, which is a list in a list, is created by creating a list, but indenting
with the list that should contain it. Since lists are block items, it must be begin and end
with empty lines. And, since this is a list it also follows the aforementioned rules
for list continuation. [unordered-sublist-example] demonstrates the syntax for creating
nested lists.

!devel! example caption=Nested unordered lists. id=unordered-sublist-example
- A
- B

  - B.1
  - B.2

    - B.2.1
    - B.2.2

  - B.3

    - B.3.1

      - B 3.1.1

    - B.3.2

  - B.4

- D
!devel-end!


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
You can create shortcuts to common items: [foo].

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
