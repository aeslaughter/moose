"""
Extension for floats such as figures, tables, and code listings
"""
import collections
import uuid

from MooseDocs.common import exceptions
from MooseDocs.base import components
from MooseDocs.extensions import core, table
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

def make_extension():
    return FloatExtension()

class Float(tokens.Token):
    pass

class Caption(tokens.CountToken):
    PROPERTIES = [Property("key", ptype=unicode)]

    def __init__(self, *args, **kwargs):
        tokens.CountToken.__init__(self, *args, **kwargs)

        if self.key:
            tokens.Shortcut(self.root, key=self.key,
                                       link=u'#{}'.format(self.key),
                                       content=u'{} {}'.format(self.prefix.title(), self.number))

class ModalLink(tokens.Link):
    PROPERTIES = [Property("title", ptype=tokens.Token, required=True),
                  Property("content", ptype=tokens.Token, required=True),
                  Property("bottom", ptype=bool, default=False)]

class FloatExtension(components.Extension):

    def extend(self, reader, renderer):
        renderer.add(Float, RenderFloat())
        renderer.add(Caption, RenderCaption())
        renderer.add(ModalLink, RenderModalLink())

    def reinit(self):
        Caption.COUNTS.clear()

class RenderFloat(components.RenderComponent):
    def createHTML(self, token, parent):
        div = html.Tag(parent, 'div', **token.attributes)
        div['class'] = 'moose-float-div'
        return div

    def createMaterialize(self, token, parent):
        div = html.Tag(parent, 'div', **token.attributes)
        div['class'] = 'card'
        return html.Tag(div, 'div', class_='card-content')

    def createLatex(self, token, parent):
        pass

class RenderCaption(components.RenderComponent):

    def createHTML(self, token, parent):
        caption = html.Tag(parent, 'p', class_="moose-caption")

        if token.prefix:
            heading = html.Tag(caption, 'span', class_="moose-caption-heading")
            html.String(heading, content=u"{} {}: ".format(token.prefix, token.number))

        text = html.Tag(caption, 'span', class_="moose-caption-text")
        return text

    def createLatex(self, token, parent):
        pass

class RenderModalLink(core.RenderLink):

    def createMaterialize(self, token, parent):
        link = core.RenderLink.createMaterialize(self, token, parent)

        tag = uuid.uuid4()
        link['class'] = 'modal-trigger'
        link['href'] = u'#{}'.format(tag)

        cls = "modal bottom-sheet" if token.bottom else "modal"
        modal = html.Tag(link.parent, 'div', class_=cls, id_=tag)
        modal_content = html.Tag(modal, 'div', class_="modal-content")

        title = html.Tag(modal_content, 'h4')
        self.translator.renderer.process(title, token.title)

        self.translator.renderer.process(modal_content, token.content)

        return link
