import os
from moosedown import base
from moosedown.extensions import core, table
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return AutoLinkExtension(**kwargs)

class AutoLinkExtension(base.Extension):

    def extend(self, reader, renderer):
        renderer.add(tokens.Link, RenderAutoLink())

#TODO: [foo.md] should create a link and use the top level heading???
class RenderAutoLink(core.RenderLink):

    def createHTML(self, token, parent):
        tag = core.RenderLink.createHTML(self, token, parent)

        #TODO: do nothing if self.translator.node is None

        href = tag['href']
        if href.endswith('.md'):
            obj = self.translator.node.findall(href, maxcount=1)
            if obj:
                tag['href'] = os.path.relpath(obj[0].local, os.path.dirname(self.translator.node.local)).replace('.md', '.html') #TODO: extensions should not be hardcoded (see page.MarkdownNode)
        return tag
