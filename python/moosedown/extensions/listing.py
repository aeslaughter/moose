"""Extension for linking to other pages"""
import os
import re
import copy
import codecs

import anytree

import moosedown
from moosedown.common import exceptions
from moosedown.base import components
from moosedown.extensions import command, floats
from moosedown.tree import tokens, html
from moosedown.tree.base import Property

def make_extension(**kwargs):
    return ListingExtension(**kwargs)

class ListingExtension(command.CommandExtension):

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['prefix'] = (u'Listing', "The caption prefix (e.g., Fig.).")
        config['height'] = (u'300px', "The default height for listings.")
        return config

    def extend(self, reader, renderer):

        self.requires(command, floats)

        self.addCommand(ListingCommand())
        #self.addCommand(VideoCommand())

        #renderer.add(Image, RenderImage())
        #renderer.add(Video, RenderVideo())

class ListingCommand(command.CommandComponent):
    COMMAND = 'listing'
    SUBCOMMAND = '*'
    #LANGUAGE = dict(py='python'

    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['language'] = (u'text', "The language to use for highlighting, if not supplied it will be infered from the extension (if possible).")
        settings['caption'] = (None, "The caption to use for the listing content.")
        settings['height'] = (u'300px', "The default height for listing content.")
        return settings

    def createToken(self, info, parent): #pylint: disable=doc-string

        # Read filename
        filename = os.path.join(moosedown.ROOT_DIR, info['subcommand'])
        if not os.path.exists(filename):
            msg = "{} does not exist."
            raise exceptions.TokenizeException(msg, filename)

        with codecs.open(filename, encoding='utf-8') as fid:
            content = fid.read()

        # Listing container
        flt = floats.Float(parent)

        # Captions
        cap = self.settings['caption']
        key = self.settings['id']
        if key:
            caption = floats.Caption(flt, key=key, prefix=self.extension['prefix'])
            if cap:
                self.translator.reader.parse(caption, cap, moosedown.INLINE)
        elif cap:
            caption = floats.Caption(flt)
            self.translator.reader.parse(caption, cap, moosedown.INLINE)

        code = tokens.Code(flt, style="height:{};".format(self.settings['height']),
                           language=self.settings['language'],
                           code=self.createContent(content))


        # TODO: OPTIONAL
        #footer = floats.Content(flt, class_='moose-listing-footer')
        a = tokens.Link(flt, url=filename, string=u'({})'.format(filename))
        modal = floats.Modal(a, bottom=True, title=filename)
        tokens.Code(modal,
                           language=self.settings['language'],
                           code=self.createContent(content))

        return parent

    def createContent(self, content):
        return content

"""
class RenderImage(components.RenderComponent):

    def createHTML(self, token, parent): #pylint: disable=doc-string
        return html.Tag(parent, 'img', src=token.src, **token.attributes)

    def createMaterialize(self, token, parent): #pylint: disable=doc-string
        return html.Tag(parent, 'img', src=token.src,
                                       class_='materialboxed moose-image center-align',
                                       **token.attributes)

class RenderImage(components.RenderComponent):

    def createHTML(self, token, parent): #pylint: disable=doc-string
        return html.Tag(parent, 'img', src=token.src, **token.attributes)

    def createMaterialize(self, token, parent): #pylint: disable=doc-string
        tag = self.createHTML(token, parent)
        tag['class'] = 'materialboxed moose-image center-align'
        return tag

class RenderVideo(components.RenderComponent):
    def createHTML(self, token, parent): #pylint: disable=doc-string
        video = html.Tag(parent, 'video', **token.attributes)
        _, ext = os.path.splitext(token.src)
        source = html.Tag(video,'source', src=token.src, type_="video/{}".format(ext[1:]))

        video['width'] = '100%'
        if token.controls:
            video['controls'] = 'controls'
        if token.autoplay:
            video['autoplay'] = 'autoplay'
        if token.loop:
            video['loop'] = 'loop'
"""
