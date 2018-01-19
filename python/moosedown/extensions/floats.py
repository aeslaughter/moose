"""
Extension for floats such as figures, tables, and code listings
"""
import collections
import uuid

from moosedown import base
from moosedown.extensions import core, table
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension():
    return FloatExtension()

class Float(tokens.Token):
    pass
    #def __init__(self, *args, **kwargs):
    #    tokens.Token.__init__(self, *args, **kwargs)
            #tokens.Word(shortcut, content=u'Example')
            #tokens.Space(shortcut)
            #tokens.Number(shortcut, content=u'42')


class Caption(tokens.Token):
    PROPERTIES = [Property("prefix", ptype=unicode, required=True),
                  Property("number", ptype=int), # set by constructor
                  Property("key", ptype=unicode)]
    COUNTS = collections.defaultdict(int)

    def __init__(self, *args, **kwargs):
        tokens.Token.__init__(self, *args, **kwargs)

        Caption.COUNTS[self.prefix] += 1
        self.number = Caption.COUNTS[self.prefix]

        if self.key:
            tokens.Shortcut(self.root, key=self.key,
                                       link=u'#{}'.format(self.key),
                                       content=u'{} {}'.format(self.prefix.title(), self.number))

class Content(tokens.Token):
    pass
    #PROPERTIES = [Property("class", ptype=unicode, required=True)]

class FloatExtension(base.Extension):

    def extend(self, reader, renderer):

        renderer.add(Content, RenderContent())
        renderer.add(Float, RenderFloat())
        renderer.add(Caption, RenderCaption())
        renderer.add(Modal, RenderModal())
        renderer.add(Tabs, RenderTabs())
        renderer.add(Tab, RenderTab())

        #renderer.add(ShortcutLink, RenderShortcutLink)

        #self.addCommand(ExampleCommand())

    def reinit(self):
        Caption.COUNTS.clear()


class Modal(tokens.Token):
    pass

class Tabs(tokens.Token):
    pass

class Tab(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True)]

class Modal(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True),
                  Property("icon", ptype=unicode)]
    pass


#class RenderShortcutLink(core.RenderShortcutLink):
#    pass
    #def createHTML()


class RenderFloat(base.RenderComponent):
    def createHTML(self, token, parent):
        attrs = token.attributes
    #    print 'ATTRS:', attrs

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
        attributes = token.attributes
        attributes.pop('class', None)
        div = html.Tag(parent, 'div', class_='card', **attributes)
        return div

class RenderContent(base.RenderComponent):
    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):
        return html.Tag(parent, 'div', **token.attributes)

class RenderCaption(base.RenderComponent):
    #__COUNTS__ = collections.defaultdict(int)

    def __init__(self, *args, **kwargs):
        base.RenderComponent.__init__(self, *args, **kwargs)
    #    self._count = collections.defaultdict(int)

    #def reinit(self):
    #    self._count.clear() #TODO: restore the reinit() method

    def createMaterialize(self, token, parent):
        tag = token.prefix.lower()
        #self._count[tag] += 1


        content = html.Tag(parent, 'div', class_="card-content")
        caption = html.Tag(content, 'p', class_="moose-caption")

        heading = html.Tag(caption, 'span', class_="moose-caption-heading")
        html.String(heading, content=u"{} {}: ".format(token.prefix, token.number))
        text = html.Tag(caption, 'span', class_="moose-caption-text")
        return text

    def createHTML(self, root, **kwargs):
        pass

    def createLatex(self, root, **kwargs):
        pass

class RenderModal(base.RenderComponent):

    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):
        tag = uuid.uuid4()

        div = html.Tag(parent, 'div', class_='moose-modal-button')
        data = {'data-tooltip':token.title, 'data-position':'top', 'data-delay':'50'}
        btn = html.Tag(div, 'a',
                       class_="tooltipped btn-floating btn-large modal-trigger",
                       href="#{}".format(tag), **data)
       # html.String(btn, content=token.title)

        if token.icon:
            icon = html.Tag(btn, 'i', class_="material-icons")
            html.String(icon, content=token.icon)

        modal = html.Tag(parent.parent, 'div', class_="modal", id_=tag)
        modal_content = html.Tag(modal, 'div', class_="modal-content")
        #heading = html.Tag(modal_content, 'h4')
        #html.Tag(heading)

        #preview = self.renderer.render(token.preview, reinit=False)
        #preview.find('body').parent = modal_content

        footer = html.Tag(modal, 'div', class_="modal-footer grey lighten-3")
        close = html.Tag(footer, 'a', class_="modal-action modal-close btn-flat")
        html.String(close, content=u'Done')

        return modal_content

class RenderTabs(base.RenderComponent):
    def createMaterialize(self, token, parent):
        if 'card' in parent['class']:
            parent = html.Tag(parent, 'div', class_="card-tabs")

        ul = html.Tag(parent, 'ul', class_="tabs")
        content = html.Tag(parent, 'div', class_='card-content grey lighten-4')
        return ul

class RenderTab(base.RenderComponent):
    def createMaterialize(self, token, parent):
        tag = uuid.uuid4()
        tab = html.Tag(parent, 'li', class_="tab")
        a = html.Tag(tab, 'a', href="#{}".format(tag))
        html.String(a, content=token.title)

        div = html.Tag(parent.parent.children[-1], 'div', id_=tag)

        return  div
