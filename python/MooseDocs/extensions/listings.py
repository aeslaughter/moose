import re
import os
import cgi
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree
from markdown.extensions.fenced_code import FencedBlockPreprocessor

import MooseDocs
from MooseDocs import MooseMarkdown
from MooseCommonExtension import MooseCommonExtension

from FactorySystem import ParseGetPot

try:
    import mooseutils.MooseSourceParser
    HAVE_MOOSE_CPP_PARSER = True
except:
    HAVE_MOOSE_CPP_PARSER = False

class ListingExtension(markdown.Extension):
    """
    Extension for adding including code and other text files.
    """
    def __init__(self, **kwargs):
        self.config = dict()
        self.config['repo'] = ['', "The remote repository to create hyperlinks."]
        self.config['make_dir'] = ['', "The location of the MakeFile for determining the include paths when using clang parser."]
        super(ListingExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds include support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        # Replace the standard fenced code to a version that handles !listing line
        if 'fenced_code_block' in md.preprocessors:
            md.preprocessors.add('fenced_code_block',
                                 ListingFencedBlockPreprocessor(md),
                                 "<fenced_code_block")

        md.inlinePatterns.add('moose-listing', ListingPattern(markdown_instance=md, **config), '_begin')

        md.inlinePatterns.add('moose-input-listing', ListingInputPattern(markdown_instance=md, **config), '_begin')

        md.inlinePatterns.add('moose-clang-listing', ListingClangPattern(markdown_instance=md, **config), '_begin')


def makeExtension(*args, **kwargs):
    return ListingExtension(*args, **kwargs)


class ListingPattern(MooseCommonExtension, Pattern):
    """
    The basic object for creating code listings from files.

    Args:
      language[str]: The code language (e.g., 'python' or 'c++')
    """
    RE = r'(?<!`)!listing\s+(?P<filename>.*\.\w+)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['strip-header'] = (True, "When True the MOOSE header is removed for display.")
        settings['caption'] = (None, "The text caption, if an empty string is provided a link to the filename is created, if None is provided no caption is applied, otherwise the text given is used.")
        settings['language'] = (None, "The language to utilize for providing syntax highlighting.")
        settings['link'] = (True, "Include a link to the filename in the caption.")
        settings['strip-extra-newlines'] = (True, "Removes extraneous new lines from the text.")
        settings['prefix'] = ('', "Text to include prior to the included text.")
        settings['suffix'] = ('', "Text to include after to the included text.")
        settings['indent'] = (0, "The level of indenting to apply to the included text.")
        settings['strip-leading-whitespace'] = (False, "When True leading white-space is removed from the included text.")
        settings['counter'] = ('listing', "The counter group to associate wit this command.")
        settings['line'] = (None, "A portion of text that unique identifies a single line to include.")
        settings['start'] = (None, "A portion of text that unique identifies the starting location for including text, if not provided the beginning of the file is utilized.")
        settings['end'] = (None, "A portion of text that unique identifies the ending location for including text, if not provided the end of the file is used. By default this line is not included in the display.")
        settings['include-end'] = (False, "When True the texted captured by the 'end' setting is included in the displayed text.")
        settings['copy-button'] = (True, "Enable/disable the inclusion of a copy button.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

        # The root/repo settings
        self._repo = kwargs.pop('repo')

    def handleMatch(self, match):
        """
        Process the text file provided.
        """
        # Update the settings from g match
        settings = self.getSettings(match.group(3))

        # Read the file
        rel_filename = match.group('filename').lstrip('/')
        filename = MooseDocs.abspath(rel_filename)
        if not os.path.exists(filename):
            return self.createErrorElement("Unable to locate file: {}".format(rel_filename))

        # Figure out file extensions
        if settings['language'] is None:
            _, ext = os.path.splitext(rel_filename)
            if ext in ['.C', '.h', '.cpp', '.hpp']:
                settings['language'] = 'c++'
            elif ext == '.py':
                settings['language'] = 'python'
            else:
                settings['language'] = 'text'

        # Extract the content from the file
        content = self.extractContent(filename, settings)
        if content == None:
            return self.createErrorElement("Failed to extract content from {}.".format(filename))

        # Apply additional settings to content
        content = self.prepareContent(content, settings)

        # Return the Element object
        el = self.createElement(content, rel_filename, settings)
        return el

    def prepareContent(self, content, settings):
        """
        Prepare the convent for conversion to Element object.

        Args:
          content[str]: The content to prepare (i.e., the file contents).
        """

        # Strip leading/trailing newlines
        content = re.sub(r'^(\n*)', '', content)
        content = re.sub(r'(\n*)$', '', content)

        # Strip extra new lines (optional)
        if settings['strip-extra-newlines']:
            content = re.sub(r'(\n{3,})', '\n\n', content)

        # Strip header
        if settings['strip-header']:
            strt = content.find('/********')
            stop = content.rfind('*******/\n')
            content = content.replace(content[strt:stop+9], '')

        # Strip leading/trailing white-space
        if settings['strip-leading-whitespace']:
            content = re.sub(r'^(\s+)', '', content, flags=re.MULTILINE)

        # Add indent
        if settings['indent'] > 0:
            lines = content.split('\n')
            content = []
            for line in lines:
                content.append('{}{}'.format(' '*int(settings['indent']), line))
            content = '\n'.join(content)

        # Prefix/suffix
        if settings['prefix']:
            content = '{}\n{}'.format(settings['prefix'], content)
        if settings['suffix']:
            content = '{}\n{}'.format(content, settings['suffix'])

        return content

    def createElement(self, content, rel_filename, settings):
        """
        Create the code element from the supplied source code content.

        Args:
          label[str]: The label supplied in the regex, [label](...)
          content[str]: The code content to insert into the markdown.
          filename[str]: The complete filename (for error checking)
          rel_filename[str]: The relative filename; used for creating github link.
          settings[dict]: The current settings.

        NOTE: The code related settings and clean up are applied in this method.
        """

        # Build outer div container
        MooseMarkdown.CODE_BLOCK_COUNT += 1
        el = self.createFloatElement(settings)

        # Build the code
        pre = etree.SubElement(el, 'pre')
        code = etree.SubElement(pre, 'code')
        if settings['language']:
            code.set('class', 'language-{}'.format(settings['language']))
        content = cgi.escape(content, quote=True)
        code.text = self.markdown.htmlStash.store(content.strip('\n'))

        # Filename link
        if settings['link']:
            link = etree.Element('div')
            a = etree.SubElement(link, 'a')
            a.set('href', os.path.join(self._repo, rel_filename))
            a.text = '({})'.format(os.path.basename(rel_filename))
            a.set('class', 'moose-listing-link tooltipped')
            a.set('data-tooltip', rel_filename)
            el.append(link)

        # Copy button
        if settings['copy-button']:
            code.set('id', 'moose-code-block-{}'.format(MooseMarkdown.CODE_BLOCK_COUNT))
            btn = self.createCopyButton(code.get('id'))
            pre.insert(0, btn)

        return el

    def extractContent(self, filename, settings):
        """
        Extract the content to display.

        Args:
            filename[str]: The absolute filename to read.
            settings[dict]: The settings for the match.
        """
        content = None
        if settings['line']:
            content = self.extractLine(filename, settings["line"])

        elif settings['start'] or settings['end']:
            content = self.extractLineRange(filename, settings['start'], settings['end'], settings['include-end'])

        else:
            with open(filename) as fid:
                content = fid.read()

        return content

    @staticmethod
    def extractLine(filename, desired):
        """
        Function for returning a single line.

        Args:
          desired[str]: The text to look for within the source file.
        """

        # Read the lines
        with open(filename) as fid:
            lines = fid.readlines()

        # Search the lines
        content = None
        for line in lines:
            if desired in line:
                content = line

        return content

    @staticmethod
    def extractLineRange(filename, start, end, include_end):
        """
        Function for extracting content between start/end strings.

        Args:
          filename[str]: The name of the file to examine.
          start[str|None]: The starting line (when None is provided the beginning is used).
          end[str|None]: The ending line (when None is provided the end is used).
          include-end[bool]: If True then the end string is included
        """

        # Read the lines
        with open(filename) as fid:
            lines = fid.readlines()

        # The default start/end positions
        start_idx = 0
        end_idx = len(lines)

        if start:
            for i in range(end_idx):
                if start in lines[i]:
                    start_idx = i
                    break
        if end:
            for i in range(start_idx, end_idx):
                if end in lines[i]:
                    end_idx = i + 1 if include_end else i
                    break

        return ''.join(lines[start_idx:end_idx])

class ListingInputPattern(ListingPattern):
    """
    Markdown extension for extracting blocks from input files.
    """
    RE = r'(?<!`)!listing\s+(?P<filename>.*\.i)(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = ListingPattern.defaultSettings()
        settings['block'] = (None, "The input file syntax block to include.")
        return settings

    def __init__(self, **kwargs):
        super(ListingInputPattern, self).__init__(**kwargs)

    def extractContent(self, filename, settings):
        """
        Extract input file content with GetPot parser if 'block' is available. (override)
        """
        if not settings['block']:
            return super(ListingInputPattern, self).extractContent(filename, settings)

        parser = ParseGetPot(filename)
        node = parser.root_node.getNode(settings['block'])
        if node is not None:
            return node.createString()

class ListingClangPattern(ListingPattern):
    """
    A markdown extension for including source code snippets using clang python bindings.

    Inputs:
      make_dir[str]: (required) The MOOSE application directory for running make command.
      **kwargs: key, value arguments passed to base class.
    """
    RE = '(?<!`)!listing\s+(?P<filename>.*\.[Ch])(?:$|\s+)(?P<settings>.*)'

    @staticmethod
    def defaultSettings():
        settings = ListingPattern.defaultSettings()
        settings['method'] = (None, "The C++ method to return using the clang parser.")
        settings['declaration'] = (False, "When True the declaration is returned, other size the definition is given.")
        return settings

    def __init__(self, **kwargs):
        super(ListingClangPattern, self).__init__(**kwargs)

        # The make command to execute
        self._make_dir = MooseDocs.abspath(kwargs.pop('make_dir'))
        if not os.path.exists(os.path.join(self._make_dir, 'Makefile')):
            log.error("Invalid path provided for make: {}".format(self._make_dir))
            raise Exception('Critical Error')

    def handleMatch(self, match):
        """
        Produce an error if the Clang parser is not setup correctly (override).
        """
        settings = self.getSettings(match.group('settings'))
        if not settings['method'] and not HAVE_MOOSE_CPP_PARSER:
            return self.createErrorElement("Failed to load python clang python bindings.")
        return super(ListingClangPattern, self).handleMatch(match)

    def extractContent(self, filename, settings):
        """
        Extract input file content with GetPot parser if 'block' is available. (override)
        """
        if not settings['method']:
            return super(ListingClangPattern, self).extractContent(filename, settings)

        try:
            parser = mooseutils.MooseSourceParser(self._make_dir)
            parser.parse(filename)
            decl, defn = parser.method(settings['method'])
            if settings['declaration']:
                return decl
            return defn
        except:
            log.error('Failed to parser file ({}) with clang for the {} method.'.format(filename, settings['method']))

class ListingFencedBlockPreprocessor(FencedBlockPreprocessor, MooseCommonExtension):
    """
    Adds the ability to proceed a fenced code block with !listing command.
    """
    LANG_TAG = ' class="language-%s"'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['caption'] = (None, "The caption text to place after the heading and number.")
        settings['counter'] = ('listing', "The name of the global counter to utilized for numbering.")
        settings['copy-button'] = (True, "Enable/disable the inclusion of a copy button.")
        return settings

    def __init__(self, markdown_instance=None, **config):
        MooseCommonExtension.__init__(self, **config)
        FencedBlockPreprocessor.__init__(self, markdown_instance)

    def run(self, lines):
        """
        Preprocess the lines by wrapping the listing <div> around the fenced code.
        """

        # Set the default cold wrapping, with the language in the <pre> block for prisim.js
        self.CODE_WRAP = '<pre%s><code>%s</code></pre>'

        # If the FENCED_BLOCK_RE is proceed by !listing wrap the results.
        text = '\n'.join(lines)
        listing_re = r'(?<!`)!listing\s*(?P<settings>.*)\n' + self.FENCED_BLOCK_RE.pattern
        match = re.search(listing_re, text, flags=re.MULTILINE|re.DOTALL|re.VERBOSE)
        if match:
            placeholder = markdown.util.HTML_PLACEHOLDER % self.markdown.htmlStash.html_counter
            settings = self.getSettings(match.group('settings'))
            div = self.createFloatElement(settings)

            if settings['copy-button']:
                code_id = 'moose-code-block-{}'.format(MooseMarkdown.CODE_BLOCK_COUNT)
                btn = self.createCopyButton(code_id)
                self.CODE_WRAP = '<pre%s>{}<code id={}>%s</code></pre>'.format(etree.tostring(btn), code_id)

            lines = super(ListingFencedBlockPreprocessor, self).run(lines)

            start = self.markdown.htmlStash.store(etree.tostring(div)[:-6], safe=True)
            end = self.markdown.htmlStash.store('</div>', safe=True)

            idx = lines.index(placeholder)
            lines.insert(idx+1, end)
            lines.insert(idx, start)

        else:
            lines = super(ListingFencedBlockPreprocessor, self).run(lines)

        return lines
