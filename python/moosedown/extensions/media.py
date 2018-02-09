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
    PROPERTIES = tokens.Token.PROPERTIES + [Property('src', required=True, ptype=unicode)]

class Video(tokens.Token):
    PROPERTIES = tokens.Token.PROPERTIES + [Property('src', required=True, ptype=unicode),
                                            Property('controls', default=True, ptype=bool),
                                            Property('autoplay', default=True, ptype=bool),
                                            Property('loop', default=True, ptype=bool)]


class MediaExtension(command.CommandExtension):
    REQUIRES = [moosedown.extensions.command, moosedown.extensions.floats] #TODO: check this

    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['prefix'] = (u'Figure', "The caption prefix (e.g., Fig.).")
        return config

    def extend(self, reader, renderer):

        self.addCommand(ImageCommand())
        self.addCommand(VideoCommand())

        renderer.add(Image, RenderImage())
        renderer.add(Video, RenderVideo())


class MediaCommandBase(command.CommandComponent):
    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the code specification example.")
        return settings

    def createMedia(self, parent, src):
        pass

    def createToken(self, info, parent): #pylint: disable=doc-string

        src = info['subcommand']

        if src.startswith('http'):
            location = src
        else:
            node = parent.root.page.findall(src, maxcount=1, mincount=1, exc=exceptions.TokenizeException)
            location = unicode(node[0].relative(parent.root.page))

        flt = floats.Float(parent, **self.attributes)
        self.createMedia(flt, location)

        cap = self.settings['caption']
        key = self.settings['id']
        if key:
            caption = floats.Caption(flt, key=key, prefix=self.extension['prefix'])
            if cap:
                self.translator.reader.parse(caption, cap, moosedown.INLINE)
        elif cap:
            caption = floats.Caption(flt)
            self.translator.reader.parse(caption, cap, moosedown.INLINE)

        return parent


class ImageCommand(MediaCommandBase):
    """
    Creates an AutoLink when *.md is detected, otherwise a core.Link token.
    """
    COMMAND = 'media'
    SUBCOMMAND = ('jpg', 'jpeg', 'gif', 'png', 'svg')

    def createMedia(self, parent, src):
        return Image(parent, src=src)


class VideoCommand(MediaCommandBase):
    COMMAND = 'media'
    SUBCOMMAND = ('ogg', 'webm', 'mp4')

    @staticmethod
    def defaultSettings():
        settings = MediaCommandBase.defaultSettings()
        settings['controls'] = (True, "Display the video player controls.")
        settings['loop'] = (False, "Automatically loop the video.")
        settings['autoplay'] = (False, "Automatically start playing the video.")
        return settings

    def createMedia(self, parent, src):
        return Video(parent, src=src, controls=self.settings['controls'],
                                      loop=self.settings['loop'],
                                      autoplay=self.settings['autoplay'])


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
