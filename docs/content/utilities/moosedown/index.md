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

## Core Extension
The core extension is the portion of the MooseDown language that is designed to mimic [markdown]
syntax. As mentioned above MooseDown is far more strict than traditional [markdown] implementations.
There for the following sections should be read in detail to understand the supported syntax,
especially if you are familiar with more general markdown formats.

### Code Blocks
Code blocks are created by enclosing the code for display in triple backticks. Settings for
the code block are defined by key-value pairings that follow the backticks.

!devel settings module=moosedown.extensions.core object=Code

!devel! spec caption=Basic fenced code block.
```language=bash
export METHOD=opt
```
~~~
<pre><code class="language-bash">
export METHOD=opt
</code></pre>
~~~
\begin{listing}3
export METHOD=opt
\end{listing}
!end!

### Quotations
Quote blocks are created by starting a line with the `>` character.g

!devel! spec caption=Basic block quote.
> This is a quotation.
~~~
<blockquote>
<p>This is a quotation.</p>
</blockquote>
~~~
\begin{quote}
This is a quotation.
\end{quote}
!end!

Quote blocks can contain any valid markdown, including other quotations.

> Foo
>
> > Another item, that also includes code.
> >
> > ```language=python
> > for i in range(10):
> >   print i
> > ```
> See, I told you.


### Headings
All headings from level 1 to 6 must be specified using the hash (`#`) character, where the
number of hashes indicate the heading level. The hash(es) must be followed by a single space.

Settings may be applied after the heading title text, the available settings include the
following.

!devel settings module=moosedown.extensions.core object=HeadingHash

!devel! spec caption=Basic use of all six heading levels.
# Level One
## Level Two
### Level Three
#### Level Four
##### Level Five
###### Level Six
~~~
<h1>Level One</h1>
<h2>Level Two</h2>
<h3>Level Three</h3>
<h4>Level Four</h4>
<h5>Level Five</h5>
<h6>Level Six</h6>
~~~
\part{Level One}
\chapter{Level Two}
\section{Level Three\label{level-three}}
\subsection{Level Four}
\subsubsection{Level Five}
\paragraph{Level Six}
!end!


!devel! spec caption=Use of settings within heading.
## Level Two style=font-size:15pt id=level-two
~~~
<h2 style="font-size:14pt" id="level-two">Level Two</h2>
~~~
\section{Level Two\label{level-two}}
!end!

### Unordered List
Unordered list items in MooseDown +must+ begin with a dash (`-`).

!devel! spec caption=Unordered list basic syntax.
- Item 1
- Item 2
~~~
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
~~~
\begin{itemize}
\item Item 1
\item Item 2
\end{itemize}
!end!

List items may contain lists, code, or any other markdown content and the item content may
span many lines. The continuation is specified by indenting the content to be included within the
item by two spaces.

!devel! spec caption=Lists can contain other markdown content.
- Item with code
  Content can be contained within a list, all valid MooseDown syntax can be used.

  ```
  foo
  ```
- Another item
~~~
<ul>
<li>
<p>Item with code Content can be contained within a list, all valid MooseDown syntax can be used.</p>
<pre><code class="language-bash">METHOD=opt</code></pre>
</li>
<li><p>Another item</p>
</li>
</ul>
~~~
LaTeX
!end!


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


!devel! spec
- Item One
- Item Two
  - Nested One
  - Nested Two
- Item Three
~~~
<ul>
  <li>Item One</li>
  <li>Item Two</li>
  <li>
    <ul>
      <li>Nested One</li>
      <li>Nested Two</li>
    </ul>
  </li>
  <li>Item Three</li>
</ul>
~~~
\begin{itemize}
  \item Item One
  \item Item Two
  \item
    \begin{itemize}
      \item Nested One  
      \item Nested Two
    \end{itemize}
  \item Item Three
\end{itemize}
!end!




### Numbered List
1. A numbered list that starts with the number provided.

   This list is also nested because it doesn't start with two empty lines.

### Text Formatting

em, strong, need to add strikethrough, underline, subscript, superscript, mark, inserted

This is ***something* with various
levels** of html formatting *that
spans* many lines. It all *should* work
fine.


[AST]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[HTML]: https://en.wikipedia.org/wiki/HTML
[CommonMark]: http://commonmark.org/
[markdown]: https://en.wikipedia.org/wiki/Markdown
