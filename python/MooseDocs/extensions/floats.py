"""
Extension for floats such as figures, tables, and code listings
"""
import collections
import uuid

from MooseDocs.base import components
from MooseDocs.extensions import core, table
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

def make_extension():
    return FloatExtension()

class Float(tokens.Token):
    pass

class Caption(tokens.CountToken):
    PROPERTIES = tokens.CountToken.PROPERTIES + [Property("key", ptype=unicode)]

    def __init__(self, *args, **kwargs):
        tokens.CountToken.__init__(self, *args, **kwargs)

        if self.key:
            tokens.Shortcut(self.root, key=self.key,
                                       link=u'#{}'.format(self.key),
                                       content=u'{} {}'.format(self.prefix.title(), self.number))

class Content(tokens.Token):
    pass
    #PROPERTIES = [Property("class", ptype=unicode, required=True)]

class FloatExtension(components.Extension):

    def extend(self, reader, renderer):

        renderer.add(Content, RenderContent())
        renderer.add(Float, RenderFloat())
        renderer.add(Caption, RenderCaption())
        renderer.add(Modal, RenderModal())
        #renderer.add(Tabs, RenderTabs())
        #renderer.add(Tab, RenderTab())

        #renderer.add(ShortcutLink, RenderShortcutLink)

        #self.addCommand(ExampleCommand())

    def reinit(self):
        Caption.COUNTS.clear()

"""
class Tabs(tokens.Token):
    pass

class Tab(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True)]
"""

class Modal(tokens.Token):
    PROPERTIES = [Property("title", ptype=unicode, required=True),
                  Property("bottom", ptype=bool, default=False)]


#class RenderShortcutLink(core.RenderShortcutLink):
#    pass
    #def createHTML()


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


class RenderContent(components.RenderComponent):
    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):
        content = html.Tag(parent, 'div', **token.attributes)
        content['class'] = 'card-content'
        return content

    def createLatex(self, token, parent):
        pass

class RenderCaption(components.RenderComponent):
    #__COUNTS__ = collections.defaultdict(int)

    def __init__(self, *args, **kwargs):
        components.RenderComponent.__init__(self, *args, **kwargs)
    #    self._count = collections.defaultdict(int)

    #def reinit(self):
    #    self._count.clear() #TODO: restore the reinit() method

    def createMaterialize(self, token, parent):


        #tag = token.prefix.lower()
        #self._count[tag] += 1


        #content = html.Tag(parent, 'div', class_="card-content")
        caption = html.Tag(parent, 'p', class_="moose-caption")

        if token.prefix:
            heading = html.Tag(caption, 'span', class_="moose-caption-heading")
            html.String(heading, content=u"{} {}: ".format(token.prefix, token.number))

        text = html.Tag(caption, 'span', class_="moose-caption-text")
        return text

    def createHTML(self, root, **kwargs):
        pass

    def createLatex(self, root, **kwargs):
        pass

class RenderModal(components.RenderComponent):

    def createHTML(self, token, parent):
        pass

    def createMaterialize(self, token, parent):
        tag = uuid.uuid4()

        # TODO: parent must be <a>
        parent['class'] = 'modal-trigger'
        parent['href'] = u'#{}'.format(tag)


        cls = "modal bottom-sheet" if token.bottom else "modal"
        modal = html.Tag(parent.parent, 'div', class_=cls, id_=tag)
        modal_content = html.Tag(modal, 'div', class_="modal-content")
        html.Tag(modal_content, 'h4', string=token.title)

        #footer = html.Tag(modal, 'div', class_="modal-footer grey lighten-3")
        #close = html.Tag(footer, 'a', string=u'Done', class_="modal-action modal-close btn-flat")

        return modal_content

        """
        div = html.Tag(parent, 'div', class_='moose-modal-button')
        data = {'data-tooltip':token.title, 'data-position':'top', 'data-delay':'50'}
        btn = html.Tag(div, 'a',
                       class_="tooltipped btn-floating btn-small modal-trigger",
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
        """

    def createLatex(self, token, parent):
        pass


class RenderTabs(components.RenderComponent):
    def createMaterialize(self, token, parent):
        if 'card' in parent['class']:
            cls = '{} {}'.format(token.get('class', ''), 'card-tabs')
            parent = html.Tag(parent, 'div', class_=cls)
            cls = 'tabs'
        else:
            cls = '{} {}'.format(token.get('class', ''), 'tabs')

        ul = html.Tag(parent, 'ul', class_=cls)
        content = html.Tag(parent, 'div', class_='card-content grey lighten-4')
        return ul

    def createLatex(self, token, parent):
        pass

class RenderTab(components.RenderComponent):
    def createMaterialize(self, token, parent):
        tag = uuid.uuid4()
        tab = html.Tag(parent, 'li', class_="tab")
        a = html.Tag(tab, 'a', href="#{}".format(tag))
        html.String(a, content=token.title)

        div = html.Tag(parent.parent.children[-1], 'div', id_=tag)

        return  div

    def createLatex(self, token, parent):
        pass
