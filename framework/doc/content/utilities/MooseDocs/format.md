# Format

The following content is for testing the automatic markdown formatting.

## Headings

### Headings can be long, so long that they cross the line limit. In this case the text should wrap around to a new line. It also must work with settings, the settings should be aligned on a new line as well. class=testing id=heading-id

## Code

```language=foo class=it should be possible to have a really long class name as well and it should wrap but it needs to be really long which is probably not likely id=code-id
The actual code should not wrap, if it did that would be bad because line endings are often important within code blocks.
```

## Shortcut and Shortcut Links

Regular shortcuts such as [CNN](https://www.cnn.com) as well as shortcut links such as [google] that require a short cut be defined somewhere in your markdown are handled.

## Monospace

It is possible to `have monospaced text within MooseDown, this text can be long and go across lines so the format option should handle
this as well`, which it does.

[google]: https://www.google.com

## Ordered Lists

1. Ordered lists begin with a number, of course the content of the item can be long so the content should wrap if needed.

   It is also possible for a list item to contain other markdown content, such as another list. For example the following
   is another list.

   1. This nested list item can also be long, it should wrap but maintain the nesting. It also contains
      a quote that should wrap as well.

      - This is another list.
      - That is in a list.

      > This is a long quote that is nested under a nested list, the content is also long so it should wrap.

   1. This is another item that is nested under the first list item.

2. This is a second item in the top-level list, it also has a lot of words so it should get automatically wrapped by format.
