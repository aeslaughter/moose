import os
from markdown.util import etree
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
import MooseDocs
from MooseCommonExtension import MooseCommonExtension


class MediaExtension(markdown.Extension):
    """
    Extension for adding media files via markdown.
    """

    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.inlinePatterns.add('moose_image', ImagePattern(markdown_instance=md, **config), '_begin')
        md.inlinePatterns.add('moose_video', VideoPattern(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return MediaExtension(*args, **kwargs)


class MediaPatternBase(MooseCommonExtension, Pattern):
    """
    Markdown extension for handling images.

    Usage:
     !image image_file.png|jpg|etc attribute=setting

    Settings:
      caption[str]: Creates a figcaption tag with the supplied text applied.

    All image filenames should be supplied as relative to the docs directory, i.e., media/my_image.png
    """

    def __init__(self, pattern, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, pattern, markdown_instance)

    def createImageElement(self, rel_filename, settings):
        """
        Create the element containing the image, this is a separate function to allow for other objects
        (i.e., MooseFigure) to utilize this class to build similar html.

        Inputs:
          rel_filename[str]: The path to the image relative to the git repository.
          settings[dict]: The settings extracted via getSettings() method.
        """
        # Read the file and create element
        filename = None
        repo = MooseDocs.abspath(rel_filename)
        local = os.path.abspath(os.path.join(os.getcwd(), rel_filename))
        if rel_filename.startswith('http'):
            filename = rel_filename
        elif os.path.exists(repo):
            filename = repo
        elif os.path.exists(local):
            filename = local
        else:
            return self.createErrorElement('File not found: {}'.format(rel_filename))

        return self.createMediaElement(filename, settings)

    def handleMatch(self, match):
        """
        process settings associated with !image markdown
        """
        rel_filename = match.group(2)
        settings = self.getSettings(match.group(3))
        return self.createImageElement(rel_filename, settings)


class ImagePattern(MediaPatternBase):
    """
    Find !image /path/to/file attribute=setting
    """
    RE = r'^!image\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, markdown_instance, **kwargs):
        super(ImagePattern, self).__init__(self.RE, markdown_instance, **kwargs)
        self._settings['caption'] = None
        self._settings['center'] = False
        for pos in ['left', 'right', 'top', 'bottom']:
            self._settings['margin-{}'.format(pos)] = 'auto'

    def createMediaElement(self, filename, settings):
        """
        Return the img tag.
        """

        # Create the figure element
        div = self.applyElementSettings(etree.Element('div'), settings)
        card = etree.SubElement(div, 'div')
        card.set('class', 'card')

        if settings['center']:
            style = card.get('style', '')
            card.set('style', 'margin-left:auto;margin-right:auto;' + style)

        img_card = etree.SubElement(card, 'div')
        img_card.set('class', 'card-image')

        img = etree.SubElement(img_card, 'img')
        img.set('src', os.path.relpath(filename, os.getcwd()))
        img.set('class', 'materialboxed')
        #img.set('style', 'margin-left:auto;margin-right:auto;margin-top:auto;margin-bottom:auto')

        # Add caption
        if settings['caption']:
            caption = etree.SubElement(card, 'div')
            p = etree.SubElement(caption, 'p')
            p.set('class', 'moose-caption')
            p.set('align', "justify")
            p.text = settings['caption']

        return div



class VideoPattern(MediaPatternBase):
    """
    Find !video /path/to/file attribute=setting
    """
    RE = r'^!video\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, markdown_instance=None, **kwargs):
        super(VideoPattern, self).__init__(self.RE, markdown_instance, **kwargs)
        self._settings['controls'] = True
        self._settings['loop'] = False
        self._settings['autoplay'] = False
        self._settings['width'] = 'auto'
        self._settings['height'] = 'auto'
        self._settings['center'] = True

    def createMediaElement(self, filename, settings):
        """
        Creates a video element.
        """
        _, ext = os.path.splitext(filename)

        center = settings.pop('center')
        v_opts = ['controls', 'loop', 'autoplay', 'width', 'height']
        v_vals = [settings.pop(v) for v in v_opts]

        div = self.applyElementSettings(etree.Element('div'), settings)
        if center:
            video = etree.SubElement(etree.SubElement(div, 'center'), 'video')
        else:
            video = etree.SubElement(div, 'video')
        for i, v in enumerate(v_opts):
            if v_vals[i]:
                if isinstance(v_vals[i], bool):
                    video.set(v, v)
                else:
                    video.set(v, v_vals[i])

        src = etree.SubElement(video, 'source')
        src.set('type', 'video/{}'.format(ext[1:]))
        src.set('src', filename)
        return div
