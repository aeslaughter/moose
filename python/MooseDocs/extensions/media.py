import os
import re
import glob
import collections

import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree

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
        md.inlinePatterns.add('moose_video', VideoPattern(markdown_instance=md, **config), '<moose_image')
        md.parser.blockprocessors.add('moose_slider', SliderBlockProcessor(md.parser, **config), '_begin')

def makeExtension(*args, **kwargs):
    return MediaExtension(*args, **kwargs)

class MediaPatternBase(MooseCommonExtension, Pattern):
    """
    Markdown extension for handling images.

    Usage:
     !media image_file.png|jpg|etc attribute=setting
    """
    COUNTER = collections.defaultdict(int)

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['caption'] = (None, "The caption text for the media element.")
        settings['card'] = (False, "Wrap the content in a materialize card.")
        settings['counter'] = ('figure', "The counter group that this media item belongs. This is used by float extension to provide numbered references. Set this to None to avoid counting.")
        return settings

    def __init__(self, pattern, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, pattern, markdown_instance)
        self._classname = kwargs.pop('classname', 'media')

    def handleMatch(self, match):
        """
        Create the element containing the image, this is a separate function to allow for other objects

        Inputs:
          rel_filename[str]: The path to the image relative to the git repository.
          settings[dict]: The settings extracted via getSettings() method.
        """

        # Extract the filename and settings from regex
        rel_filename = match.group(2)
        settings = self.getSettings(match.group('settings'))
        cname = settings['counter']

        # Determine the filename
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

        # Create the outer <div> tag
        div = self.applyElementSettings(etree.Element('div'), settings)
        div.set('class', 'moose-{}-div'.format(self._classname))
        if cname is not None:
            div.set('data-moose-count-{}'.format(cname), str(self.COUNTER[cname] + 1))

        # Add content and wrap within card elements
        element = div
        if settings['card']:
            element = etree.SubElement(div, 'div')
            element.set('class', 'card')
            element.set('style', 'margin-left:auto;margin-right:auto;')

        # Add media content
        media_element = self.createMediaElement(filename, settings)
        self._cardWrapper(element, media_element, 'card-image', settings)

        # Add caption
        caption_element = self.createCaptionElement(settings)
        if caption_element:
            self._cardWrapper(element, caption_element, 'card-content', settings)

        if cname is not None:
            self.COUNTER[cname] += 1
        return div

    def _cardWrapper(self, parent, child, class_, settings):
        """
        Helper for optionally wrapping a materialize 'card'
        """
        if settings['card']:
            card_element = etree.SubElement(parent, 'div')
            card_element.set('class', class_)
            card_element.append(child)
        else:
            parent.append(child)

    def createMediaElement(self, filename, settings):
        """
        Return the actual media content.
        """
        raise mooseutils.MooseException('The createMediaElement method must be overridden.')

    def createCaptionElement(self, settings):
        """
        Return the caption element.
        """
        return MooseDocs.extensions.caption_element(text=settings['caption'],
                                                    class_='moose-{}-caption'.format(self._classname))


class ImagePattern(MediaPatternBase):
    """
    Find !image /path/to/file attribute=setting
    """
    RE = r'^!media\s+(.*?)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MediaPatternBase.defaultSettings()
        settings['materialboxed'] = (True, "Create Materialize boxed content.")
        return settings

    def __init__(self, markdown_instance, **kwargs):
        kwargs.setdefault('classname', 'image')
        super(ImagePattern, self).__init__(self.RE, markdown_instance, **kwargs)

    def createMediaElement(self, filename, settings):
        """
        Return the img tag.
        """
        img = etree.Element('img')
        img.set('src', os.path.relpath(filename, os.getcwd()))
        if settings['materialboxed']:
            img.set('class', 'materialboxed')
            if settings['caption']:
                img.set('data-caption', settings['caption'])

        return img

class VideoPattern(MediaPatternBase):
    """
    Find !media /path/to/file attribute=setting

    Creates a <video> tag for webm, ogg, or mp4 extensions.
    """
    RE = r'^!media\s+(.*?(webm|ogg|mp4))(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MediaPatternBase.defaultSettings()
        settings['controls'] = (True, "Display the video player controls.")
        settings['loop'] = (False, "Automatically loop the video.")
        settings['autoplay'] = (False, "Automatically start playing the video.")
        settings['video-width'] = ('auto', "The width of the video player.")
        settings['video-height'] = ('auto', "The height of the video player.")
        settings['caption'] = (None, "The text for the video caption.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        kwargs.setdefault('classname', 'video')
        super(VideoPattern, self).__init__(self.RE, markdown_instance, **kwargs)

    def createMediaElement(self, filename, settings):
        """
        Creates a video element.
        """
        _, ext = os.path.splitext(filename)

        # HTML5 video tag can accept non-paired attributes, which is not supported by the etree
        # markdown util. However, the video tag does support "control=control" for legacy purposes,
        # so that is what is done here.
        v_opts = dict()
        v_opts['controls'] = settings.pop('controls')
        v_opts['loop'] = settings.pop('loop')
        v_opts['autoplay'] = settings.pop('autoplay')
        v_opts['width'] = settings.pop('video-width')
        v_opts['height'] = settings.pop('video-height')

        video = etree.Element('video')
        for key, value in v_opts.iteritems():
            if value:
                if isinstance(value, bool):
                    video.set(key, key)
                else:
                    video.set(key, value)

        src = etree.SubElement(video, 'source')
        src.set('type', 'video/{}'.format(ext[1:]))
        src.set('src', filename)
        return video

class SliderBlockProcessor(BlockProcessor, MooseCommonExtension):
    """
    Markdown extension for showing a Materialize carousel of images.
    Markdown syntax is:

     !slider <options>
       images/intro.png <image_options> caption=Some caption <caption_options>
       images/more*.png

    Where <options> are key=value pairs.
    Valid options are standard CSS options (images are set as background images).

    It is assumed image names will have the same filepath as on the webserver.
    """

    RE = re.compile(r'^!\ ?slider(?P<settings>.*)')

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['caption'] = (None, "The text for the slider caption.")
        return settings


    ImageInfo = collections.namedtuple('ImageInfo', 'filename img_settings caption_settings')

    def __init__(self, parser, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        BlockProcessor.__init__(self, parser)

    def parseFilenames(self, filenames_block):
        """
        Parse a set of lines with filenames, image options, and optional captions.
        Filenames can contain wildcards and glob will be used to expand them.
        Any CSS styles after the filename (but before caption if it exists)
        will be applied to the image (image is set as a background in slider).
        CSS styles listed after the caption will be applied to it.
        Expected input is similar to:
          images/1.png caption=My caption color=blue
          images/2.png background-color=gray caption= Another caption color=red
          images/other*.png
        Input:
         filenames_block[str]: String block to parse
        Return:
         list of list of dicts. The list has an entry for each image (including
         one for each expanded image from glob), each entry contains:
         1. dict of "path" which is the filename path
         2. dict of attributes to be applied to the image
         3. dict of attributes to be applied to the caption
         Each image will default to fit the slideshow window with white background
         and no caption if no options are specified.
        """
        lines = filenames_block.split("\n")
        files = []
        regular_expression = re.compile(r'(.*?\s|.*?$)(.*?)(caption.*|$)')
        for line in lines:
            line = line.strip()
            matches = regular_expression.search(line)
            fname = matches.group(1).strip()

            # Build separate dictionaries for the image and caption
            img_settings = self.getSettings(matches.group(2).strip())
            img_settings.setdefault('background-size', 'contain')
            img_settings.setdefault('background-repeat', 'no-repeat')
            img_settings.setdefault('background-color', 'white')
            caption_settings = self.getSettings(matches.group(3).strip())

            new_files = glob.glob(MooseDocs.abspath(fname))
            if not new_files:
                log.error('Parser unable to detect file(s) {} in media.py'.format(fname))
                return []
            for f in new_files:
                files.append(SliderBlockProcessor.ImageInfo(os.path.relpath(f), img_settings, caption_settings))

        return files

    def test(self, parent, block):
        """
        Test to see if we should process this block of markdown.
        Inherited from BlockProcessor.
        """
        return self.RE.search(block)

    def run(self, parent, blocks):
        """
        Called when it is determined that we can process this block.
        This will convert the markdown into HTML
        """

        block = blocks.pop(0)
        match = self.RE.search(block)
        settings = self.getSettings(match.group(1))

        slider = etree.SubElement(parent, 'div')
        slider.set('class', 'slider moose-slider-div')
        self.applyElementSettings(slider, settings)

        ul = etree.SubElement(slider, 'ul')
        ul.set('class', 'slides')

        for item in self.parseFilenames(block[match.end()+1:]):
            li = etree.SubElement(ul, 'li')
            img = etree.SubElement(li, 'img')
            img.set('src', item.filename)
            self.applyElementSettings(img, item.img_settings, keys=item.img_settings.keys())

            #Add the caption and its options if they exist
            if len(item[2]) != 0:
                caption = etree.SubElement(li, 'div')
                caption.set('class','caption')
                caption.text = item.caption_settings.pop('caption', '')
                caption = self.applyElementSettings(caption, item.caption_settings, keys=item.caption_settings.keys())


        caption = MooseDocs.extensions.caption_element(text=settings['caption'])
        slider.append(caption)
