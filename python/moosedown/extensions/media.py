"""Extension for linking to other pages"""
import os
import re
import copy

import anytree

import moosedown
from moosedown.common import exceptions
from moosedown.base import components
from moosedown.extensions import command, floats
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return MediaExtension(**kwargs)

class Image(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + [Property('src', required=True, ptype=str)]

class MediaExtension(command.CommandExtension):
    REQUIRES = [moosedown.extensions.command, moosedown.extensions.floats] #TODO: check this

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['prefix'] = (u'Figure', "The caption prefix (e.g., Fig.).")
        return config

    def extend(self, reader, renderer):

        self.addCommand(ImageCommand())
        renderer.add(Image, RenderImage())

class ImageCommand(command.CommandComponent):
    """
    Creates an AutoLink when *.md is detected, otherwise a core.Link token.
    """
    COMMAND = 'media'
    SUBCOMMAND = ('jpg', 'jpeg', 'gif', 'png', 'svg')

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        return settings

    def createToken(self, info, parent): #pylint: disable=doc-string

        src = info['filename']
        node = parent.root.page.findall(src, maxcount=1, mincount=1, exc=exceptions.TokenizeException)

        location = os.path.relpath(node[0].local, os.path.dirname(parent.root.page.local))
        print 'LOCATION:', location

        flt = floats.Float(parent, **self.attributes)
        Image(flt, src=location)

        if self.settings['caption'] and self.settings['id']:
            floats.Caption(flt, caption=self.settings['caption'],
                                prefix=self.extension['prefix'],
                                key=self.settings['id'])
        return parent

class RenderImage(components.RenderComponent):

    def createHTML(self, token, parent): #pylint: disable=doc-string
        return html.Tag(parent, 'img', src=token.src, **token.attributes)

    def createMaterialize(self, token, parent): #pylint: disable=doc-string
        return html.Tag(parent, 'img', src=token.src,
                                       class_='materialboxed moose-image center-align',
                                       **token.attributes)
