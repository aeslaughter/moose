## Motivation
[markdown] is ubiquitous as a short-hand [HTML] format, especially among software developers.
However, no standard exists and the original implementation was incomplete. Currently, there are
myriad implementations---often deemed "flavors"---of Markdown. [CommonMark](http://commonmark.org/)
is a proposed standard. However, this specification is syntactically loose. For example, when
defining lists the spacing is can be misleading, see [Example 273](http://spec.commonmark.org/0.28/#example-273) and [Example 268](http://spec.commonmark.org/0.28/#example-268) shows that some poorly defined behavior still
exists and it is stated that the associated rule "should prevent most spurious list captures."

[AST]: https://en.wikipedia.org/wiki/Abstract_syntax_tree
[HTML]: https://en.wikipedia.org/wiki/HTML
[CommonMark]: http://commonmark.org/
[markdown]: https://en.wikipedia.org/wiki/Markdown
