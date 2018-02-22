import os
import MooseDocs
from MooseDocs.base import components
from MooseDocs.extensions import command
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

#pylint: disable=doc-string

def make_extension(**kwargs):
    return AlertExtension(**kwargs)

class AlertToken(tokens.Token):
    PROPERTIES = [Property('brand', ptype=unicode, required=True),
                  Property('prefix', default=True, ptype=bool),
                  Property('title', ptype=tokens.Token)]

class AlertExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = command.CommandExtension.defaultConfig()
        config['use-title-prefix'] = (True, "Enable/disable including the brand (e.g., ERROR) as " \
                                            "prefix for the alert title.")
        return config

    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(AlertCommand())
        renderer.add(AlertToken, RenderAlertToken())

class AlertCommand(command.CommandComponent):
    COMMAND = 'alert'
    SUBCOMMAND = ('error', 'warning', 'note')

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['title'] = (None, "The optional alert title.")
        settings['prefix'] = (None, "Enable/disable the title being prefixed with the alert brand.")
        return settings

    def createToken(self, info, parent):
        title = self.settings.pop('title', None)
        brand = info['subcommand']

        if title:
            title_root = tokens.Token(None)
            self.reader.parse(title_root, title, MooseDocs.INLINE)
        else:
            title_root = None

        if self.settings['prefix'] is not None:
            prefix = self.settings['prefix']
        else:
            prefix = self.extension['use-title-prefix']

        return AlertToken(parent, brand=brand, prefix=prefix, title=title_root)

class RenderAlertToken(components.RenderComponent):

    def createTitle(self, parent, token):

        title = None
        if token.prefix or token.title:
            title = html.Tag(parent, 'div', class_='moose-alert-title')

            prefix = None
            if token.prefix:
                prefix = html.Tag(title, 'span', string=token.brand,
                                  class_='moose-alert-title-brand')

            if token.title:
                if prefix:
                    prefix(0).content += u':'

                self.translator.renderer.process(title, token.title)
        return title

    def createHTML(self, token, parent):
        div = html.Tag(parent, 'div', class_='moose-alert moose-alert-{}'.format(token.brand))
        self.createTitle(div, token)
        content = html.Tag(div, 'div', class_='moose-alert-content')
        return content

    def createMaterialize(self, token, parent):
        card = html.Tag(parent, 'div', class_='card moose-alert moose-alert-{}'.format(token.brand))
        card_content = html.Tag(card, 'div', class_='card-content')
        title = self.createTitle(card_content, token)
        if title:
            title['class'] = 'card-title'
        content = html.Tag(card_content, 'div', class_='moose-alert-content')
        return content

    def createLatex(self, token, parent):
        pass
