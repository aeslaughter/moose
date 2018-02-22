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

class Modal(tokens.Token):
    PROPERTIES = [Property("title", ptype=tokens.Token, required=True),
                  Property("bottom", ptype=bool, default=False)]

class FloatExtension(components.Extension):

    def extend(self, reader, renderer):
        renderer.add(Float, RenderFloat())
        renderer.add(Caption, RenderCaption())
        renderer.add(Modal, RenderModal())

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

class RenderModal(components.RenderComponent):

    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):
        tag = uuid.uuid4()

        #if parent.name != 'a':
        #    msg = "The Modal token must be attached to a link (e.g., and <a> tag), but a {} is " \
        #          "being used."
        #    raise exceptions.RenderException(msg, parent.name)

        parent['class'] = 'modal-trigger'
        parent['href'] = u'#{}'.format(tag)

        cls = "modal bottom-sheet" if token.bottom else "modal"
        modal = html.Tag(parent.parent, 'div', class_=cls, id_=tag)
        modal_content = html.Tag(modal, 'div', class_="modal-content")
        title = html.Tag(modal_content, 'h4')
        self.translator.renderer.process(title, token.title)

        return modal_content

    def createLatex(self, token, parent):
        pass
