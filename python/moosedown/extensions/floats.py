"""
Extension for floats such as figures, tables, and code listings
"""
import collections

from moosedown import base
from moosedown.extensions import core
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension():
    return FloatMarkdownExtension(), FloatRenderExtension()

class Float(tokens.Token):
    pass

class Caption(tokens.Token):
    PROPERTIES = [Property("prefix", ptype=unicode, required=True)]

class FloatContent(tokens.Token):
    pass


class FloatMarkdownExtension(base.MarkdownExtension):
    def extend(self):
        pass
        #self.addCommand(ExampleCommand())

class Modal(tokens.Token):
    pass

class Tabs(tokens.Token):
    pass

class Tab(tokens.Token):
    pass

"""
class FloatComponent(core.MarkdownCommandComponent):
    pass
"""


class FloatRenderExtension(base.RenderExtension):
    def extend(self):
        self.add(Float, RenderFloat())
        self.add(Caption, RenderCaption())


class RenderFloat(base.RenderComponent):
    def createHTML(self, token, parent):
        attrs = token.attributes
        if attrs['class'] is not None:
            attrs['class'] = 'moose-float-div'
        div = html.Tag(parent, 'div', **attrs)

        """
        if token.caption:
            self._count[token.label] += 1
            caption = html.Tag(div, 'p', class_="moose-caption")
            heading = html.Tag(caption, 'span', class_="moose-caption-heading")
            html.String(heading, content=u'{} {}: '.format(token.label.title(), self._count[token.label]))
            text = html.Tag(caption, 'span', class_="moose-caption-text")
            #html.String(text, content=unicode(token.caption))
        """

        return div


    def createMaterialize(self, token, parent):
        div = html.Tag(parent, 'div', class_='card')
        return div


class RenderCaption(base.RenderComponent):
    #__COUNTS__ = collections.defaultdict(int)

    def __init__(self, *args, **kwargs):
        base.RenderComponent.__init__(self, *args, **kwargs)
        self._count = collections.defaultdict(int)

    def reinit(self):
        self._count.clear()

    def createMaterialize(self, token, parent):
        tag = token.prefix.lower()
        self._count[tag] += 1

        content = html.Tag(parent, 'div', class_="card-content")
        caption = html.Tag(content, 'p', class_="moose-caption")
        heading = html.Tag(caption, 'span', class_="moose-caption-heading")
        html.String(heading, content=u"{} {}: ".format(token.prefix, self._count[tag]))
        text = html.Tag(caption, 'span', class_="moose-caption-text")
        return text

    def createHTML(self, root, **kwargs):
        pass

    def createLatex(self, root, **kwargs):
        pass
