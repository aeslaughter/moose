#!/usr/bin/env python
import re
from MooseMarkdown import MooseMarkdown

import tree

if __name__ == '__main__':


    with open('spec.md', 'r') as fid:
        md = fid.read()

    markdown = MooseMarkdown()
    ast = markdown.ast(md)
    #print ast

    html = markdown.convert()#'heading.md')
    #print html

    with open('index.html', 'w') as fid:
        fid.write(html.write())


"""
- Setup config file
- Create text/file node
- Create an !alert command (alert extension)
- Create errors by creating an alert token
- Build unittests for tokens, lexer, grammer, etc.
- Get list into single regex (unordered vs. ordered)
- Switch to _italic_ and *bold*
- Define other format __underline__, -strike through-,
- Define punctuation -- ---
- _{foo} and ^{foo} sub and superscript
"""
