"""Extension for linking to other pages"""
import os
import re
import copy

import anytree

import MooseDocs
from MooseDocs.common import exceptions
from MooseDocs.base import components
from MooseDocs.extensions import command, floats
from MooseDocs.tree import tokens, html
from MooseDocs.tree.base import Property

# Documenting all of the following classes is excessive
#pylint: disable=doc-string

def make_extension(**kwargs):
    return MediaExtension(**kwargs)

class Image(tokens.Token):
    PROPERTIES = [Property('src', required=True, ptype=unicode)]

class Video(tokens.Token):
    PROPERTIES = [Property('src', required=True, ptype=unicode),
                  Property('controls', default=True, ptype=bool),
                  Property('autoplay', default=True, ptype=bool),
                  Property('loop', default=True, ptype=bool)]

class MediaExtension(command.CommandExtension):
    @staticmethod
    def defaultConfig():
        config = components.Extension.defaultConfig()
        config['prefix'] = (u'Figure', "The caption prefix (e.g., Fig.).")
        return config

    def extend(self, reader, renderer):
        self.requires(command, floats)

        self.addCommand(ImageCommand())
        self.addCommand(VideoCommand())

        renderer.add(Image, RenderImage())
        renderer.add(Video, RenderVideo())

class MediaCommandBase(command.CommandComponent):
    @staticmethod
    def defaultSettings():
        settings = command.CommandComponent.defaultSettings()
        settings['caption'] = (None, "The caption to use for the media content.")
        return settings

    def createMedia(self, parent, src):
        pass # a required method for base classes

    def createToken(self, info, parent):

        # Determine the location of the media
        src = info['subcommand']
#        if src.startswith('http') or parent.root.page is None:
        if src.startswith('http') or self.translator.current is None:
            location = src
        else:
            #node = parent.root.page.findall(src, maxcount=1, mincount=1, exc=exceptions.TokenizeException)
            node = self.translator.current.findall(src, exc=exceptions.TokenizeException)
            location = unicode(node.relative(self.translator.current))

        # Create the float and insert the media content
        flt = floats.Float(parent, **self.attributes)
        self.createMedia(flt, location)

        # Add caption
        cap = self.settings['caption']
        key = self.settings['id']
        if key:
            caption = floats.Caption(flt, key=key, prefix=self.extension['prefix'])
            if cap:
                self.translator.reader.parse(caption, cap, MooseDocs.INLINE)
        elif cap:
            caption = floats.Caption(flt)
            self.translator.reader.parse(caption, cap, MooseDocs.INLINE)

        return parent

class ImageCommand(MediaCommandBase):
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

    def createHTML(self, token, parent):
        return html.Tag(parent, 'img', src=token.src, **token.attributes)

    def createMaterialize(self, token, parent):
        tag = self.createHTML(token, parent, **token.attributes)
        tag['class'] = 'materialboxed moose-image'
        return tag

    def createLatex(self, token, parent):
        pass

class RenderVideo(components.RenderComponent):
    def createHTML(self, token, parent):
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

    def createLatex(self, token, parent):
        pass
