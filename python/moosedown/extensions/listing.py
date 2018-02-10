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

#class ListingToken(tokens.Token):
#    PROPERTIES = tokens.Token.PROPERTIES + [Property('link', default=True)]

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
        settings['height'] = (u'350px', "The default height for listing content.")
        settings['link'] = (True, "Include a link to the filename after the listing.")
        settings['prefix'] = ('', "Text to include prior to the included text.")
        settings['suffix'] = ('', "Text to include after to the included text.")
        settings['indent'] = (0, "The level of indenting to apply to the included text.")
        settings['strip-header'] = (True, "When True the MOOSE header is removed for display.")
        settings['strip-extra-newlines'] = (True, "Removes extraneous new lines from the text.")
        settings['strip-leading-whitespace'] = (False, "When True leading white-space is removed "
                                                       "from the included text.")
        settings['line'] = (None, "A portion of text that unique identifies a single line to "
                                  "include.")
        settings['re'] = (False, "Extract content via a regex, if the 'content' group exists it is used as the desired content, otherwise group 0 is used.")
        settings['re-flags'] = ('re.MULTILINE|re.DOTALL|re.UNICODE', "Python re flags.")
        settings['start'] = (None, "A portion of text that unique identifies the starting "
                                   "location for including text, if not provided the beginning "
                                   "of the file is utilized.")
        settings['end'] = (None, "A portion of text that unique identifies the ending location "
                                 "for including text, if not provided the end of the file is "
                                 "used. By default this line is not included in the display.")
        settings['include-start'] = (True, "When False the texted captured by the 'start' setting "
                                           "is excluded in the displayed text.")
        settings['include-end'] = (False, "When True the texted captured by the 'end' setting is "
                                          "included in the displayed text.")
        #TODO: add regex
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
                           code=self.extractContent(content, self.settings))

        # Add bottom modal
        if self.settings['link']:
            a = tokens.Link(flt, url=filename, string=u'({})'.format(filename))
            modal = floats.Modal(a, bottom=True, title=filename)
            tokens.Code(modal, language=self.settings['language'],
                        code=content)

        return parent


    def extractContent(self, content, settings):


        if settings['re']:
            match = re.search(settings['re'], content, flags=eval(settings['re-flags']))
            if match:
                if 'content' in match.groupdict():
                    content = match.group('content')
                else:
                    content = match.group()
            else:
                msg = "Failed to match regular expression: {}"
                raise exceptions.TokenizeException(message, settings['re'])

        elif settings['line']:
            content = self.extractLine(content, settings["line"])

        elif settings['start'] or settings['end']:
            content = self.extractLineRange(content,
                                            settings['start'],
                                            settings['end'],
                                            settings['include-start'],
                                            settings['include-end'])

        return self.createContent(content, settings)

    def createContent(self, content, settings):

        # Strip leading/trailing newlines
        content = re.sub(r'^(\n*)', '', content)
        content = re.sub(r'(\n*)$', '', content)

        # Strip extra new lines (optional)
        if settings['strip-extra-newlines']:
            content = re.sub(r'(\n{3,})', '\n\n', content)

        # Strip header
        if settings['strip-header']:
            content = re.sub('^((?:/{2}|#)\*.*?$)', '', content, flags=re.MULTILINE)

        # Strip leading/trailing white-space
        if settings['strip-leading-whitespace']:
            content = re.sub(r'^(\s+)', '', content, flags=re.MULTILINE)

        # Add indent
        if settings['indent'] > 0:
            content = re.sub(r'^(.*?)$', '{}\1'.format(' '*int(settings['indent']), content))
            """
            lines = content.split('\n')
            c = []
            for line in lines:
                c.append('{}{}'.format(' '*int(settings['indent']), line))
            content = '\n'.join(c)
            """

        # Prefix/suffix
        if settings['prefix']:
            content = re.sub(r'^(.*?)$', '\1{}'.format(settings['prefix']), content)
            #content = '{}\n{}'.format(settings['prefix'], content)
        if settings['suffix']:
            content = re.sub(r'^(.*?)$', '{}\1'.format(settings['suffix']), content)
            #content = '{}\n{}'.format(content, settings['suffix'])

        return content

    @staticmethod
    def extractLine(content, desired):
        """
        Function for returning a single line.

        Args:
          desired[str]: The text to look for within the source file.
        """

        lines = content.split('\n')

        # Search the lines
        content = None
        for line in lines:
            if desired in line:
                content = line

        return content

    @staticmethod
    def extractLineRange(content, start, end, include_start, include_end, regex):
        """
        Function for extracting content between start/end strings.

        Args:
          filename[str]: The name of the file to examine.
          start[str|None]: The starting line (when None is provided the beginning is used).
          end[str|None]: The ending line (when None is provided the end is used).
          include-start[bool]: If True then the start string is included
          include-end[bool]: If True then the end string is included
        """
        lines = content.split('\n')

        # Read the lines
        #with open(filename) as fid:
        #    lines = fid.readlines()

        # The default start/end positions
        start_idx = 0
        end_idx = len(lines)

        if start:
            for i in range(end_idx):
                if start in lines[i]:
                    start_idx = i if include_start else i+1
                    break
        if end:
            for i in range(start_idx, end_idx):
                if end in lines[i]:
                    end_idx = i + 1 if include_end else i
                    break

        return ''.join(lines[start_idx:end_idx])


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
