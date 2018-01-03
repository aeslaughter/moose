import os
from moosedown import base
from moosedown.extensions import core, table
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension():
    return None, AutoLinkRenderExtension()

class AutoLinkRenderExtension(base.RenderExtension):

    def extend(self):
        self.add(tokens.Link, RenderAutoLink())


class RenderAutoLink(core.RenderLink):

    def createHTML(self, token, parent):
        tag = core.RenderLink.createHTML(self, token, parent)


        #TODO: do nothing if self.translator.node is None

        href = tag['href']
        if href.endswith('.md'):
            obj = self.translator.node.findall(href, maxcount=1)[0]
            tag['href'] = os.path.relpath(obj.local, os.path.dirname(self.translator.node.local)).replace('.md', '.html') #TODO: extensions should not be hardcoded (see page.MarkdownNode)
        return tag
