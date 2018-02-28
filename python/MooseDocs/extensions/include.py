"""
Create !include command for importing content.
"""
import re

from MooseDocs import common
from MooseDocs.common import exceptions
from MooseDocs.base import components
from MooseDocs.extensions import command
from MooseDocs.tree import tokens, page
from MooseDocs.tree.base import Property

# Documenting all these classes is far to repeative and useless.
#pylint: disable=missing-docstring,unused-variable

#class IncludeToken(tokens.Token):
    #PROPERTIES = [Property("include", ptype=page.MarkdownNode, required=True)]
 #   PROPERTIES = [Property('include', ptype=unicode, require=True)

def make_extension(**kwargs):
    return IncludeExtension(**kwargs)

class IncludeExtension(command.CommandExtension):


    def extend(self, reader, renderer):
        self.requires(command)
        self.addCommand(IncludeCommand())
        #renderer.add(IncludeToken, RenderInclude())

class IncludeCommand(command.CommandComponent):
    COMMAND = 'include'
    SUBCOMMAND = 'md'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['re'] = (None, "Extract content via a regex, if the 'content' group exists it " \
                                 "is used as the desired content, otherwise group zero is used.")
        settings['re-flags'] = ('re.M|re.S|re.U', "Regular expression flags commands pass to the Python re module.")
        return settings

    def createToken(self, info, parent):
        master_page = self.translator.current #parent.root.page
        include_page = master_page.findall(info['subcommand'], exc=exceptions.TokenizeException)[0]

        content = common.read(include_page.source) #TODO: copy existing tokens
        if self.settings['re']:
            content = common.regex(self.settings['re'], content, eval(self.settings['re-flags']))

        self.translator.reader.parse(parent, content)
        return parent

#class RenderInclude(components.RenderComponent):
#    """Render the included content."""
#
#    def create(self, token, parent):
#        ast = token.include.ast()
#        for child in ast:
#            self.translator.renderer.process(parent, child)
#
#    def createHTML(self, token, parent):
#        return self.create(token, parent)
#
#    def createLatex(self, token, parent):
#        return self.create(token, parent)
