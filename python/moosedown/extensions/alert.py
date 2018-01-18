import os
from moosedown import base
from moosedown.extensions import command
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return AlertExtension(**kwargs)

class Alert(tokens.Token):
    PROPERTIES = [Property('brand', ptype=str, required=True)]

class AlertTitle(tokens.Token):
    pass
#    PROPERTIES = [Property('brand', ptype=str, required=True)]

class AlertContent(tokens.Token):
    pass

class AlertExtension(base.Extension):

    def extend(self, reader, renderer):
        reader.addCommand(ErrorAlertCommand())
        reader.addCommand(WarningAlertCommand())
        reader.addCommand(NoteAlertCommand())

        renderer.add(Alert, RenderAlert())
        renderer.add(AlertTitle, RenderAlertTitle())
        renderer.add(AlertContent, RenderAlertContent())

class AlertCommandBase(command.BlockCommand):
    COMMAND = 'alert'

    @staticmethod
    def defaultSettings():
        settings = command.MarkdownCommandComponent.defaultSettings()
        settings['title'] = (None, "The optional alert title.")
        return settings

    def createToken(self, match, parent):
        title = self.settings.pop('title', None)
        alert = Alert(parent, brand=self.SUBCOMMAND, **self.settings)

        title_token = AlertTitle(alert)
        if title:
            grammer = self.reader.lexer.grammer('inline')
            self.reader.lexer.tokenize(title_token, grammer, title, match.line)

        content = AlertContent(alert)
        grammer = self.reader.lexer.grammer('block')
        self.reader.lexer.tokenize(content, grammer, match['content'], match.line)
        return alert

class ErrorAlertCommand(AlertCommandBase):
    SUBCOMMAND = 'error'

class WarningAlertCommand(AlertCommandBase):
    SUBCOMMAND = 'warning'

class NoteAlertCommand(AlertCommandBase):
    SUBCOMMAND = 'note'


class RenderAlert(base.RenderComponent):
    def createMaterialize(self, token, parent):
        card = html.Tag(parent, 'div', class_='card moose-alert moose-alert-{}'.format(token.brand))
        return html.Tag(card, 'div', class_='card-content'.format(token.brand))

class RenderAlertTitle(base.RenderComponent):
    def createMaterialize(self, token, parent):
        div = html.Tag(parent, 'div', class_='card-title moose-alert-title')
        brand = html.Tag(div, 'span', class_='moose-alert-title-brand')
        html.String(brand, content=unicode(token.parent.brand))
        return div

class RenderAlertContent(base.RenderComponent):
    def createMaterialize(self, token, parent):
        return html.Tag(parent, 'div', class_='moose-alert-content')
