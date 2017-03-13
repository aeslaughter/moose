"""
Syntax for including MOOSE source and input files.
"""
import re
import os
import cgi
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree

import MooseDocs
from MooseCommonExtension import MooseCommonExtension

from FactorySystem import ParseGetPot

try:
    import mooseutils.MooseSourceParser
    HAVE_MOOSE_CPP_PARSER = True
except:
    HAVE_MOOSE_CPP_PARSER = False

class IncludeExtension(markdown.Extension):
    """
    Extension for adding bibtex style references and bibliographies to MOOSE flavored markdown.xk
    """
    def __init__(self, **kwargs):
        self.config = dict()
        self.config['repo'] = ['', "The remote repository to create hyperlinks."]
        self.config['make_dir'] = ['', "The location of the MakeFile for determining the include paths when using clang parser."]
        super(IncludeExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds include support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.inlinePatterns.add('moose_input_block', InputPattern(markdown_instance=md, **config), '_begin')
        md.inlinePatterns.add('moose_cpp_method', ClangPattern(markdown_instance=md, **config), '_begin')
        md.inlinePatterns.add('moose_text', TextPattern(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs):
    return IncludeExtension(*args, **kwargs)


class TextPatternBase(MooseCommonExtension, Pattern):
    """
    Base class for pattern matching text blocks.

    Args:
      regex: The string containing the regular expression to match.
      language[str]: The code language (e.g., 'python' or 'c++')
    """

    def __init__(self, pattern, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, pattern, markdown_instance)

        # The root/repo settings
        self._repo = kwargs.pop('repo')

        # The default settings
        self._settings['strip_header'] = True
        self._settings['repo_link'] = True
        self._settings['label'] = True
        self._settings['language'] = 'text'
        self._settings['strip-extra-newlines'] = False
        self._settings['prefix'] = ''
        self._settings['suffix'] = ''
        self._settings['indent'] = 0
        self._settings['strip-leading-whitespace'] = False

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
        if settings['strip_header']:
            strt = content.find('/********')
            stop = content.rfind('*******/\n')
            content = content.replace(content[strt:stop+9], '')

        # Strip leading white-space
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

    def createElement(self, label, content, filename, rel_filename, settings):
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

        # Strip extra new lines
        content = self.prepareContent(content, settings)

        # Build outer div container
        el = self.applyElementSettings(etree.Element('div'), settings)
        el.set('class', 'moosedocs-code-div')

        # Build label
        if settings['repo_link'] and self._repo:
            title = etree.SubElement(el, 'a')
            title.set('href', os.path.join(self._repo, rel_filename))
        else:
            title = etree.SubElement(el, 'div')

        if settings['label']:
            title.text = label

        # Build the code
        pre = etree.SubElement(el, 'pre')
        code = etree.SubElement(pre, 'code')
        if settings['language']:
            code.set('class', settings['language'])
        content = cgi.escape(content, quote=True)
        code.text = self.markdown.htmlStash.store(content.strip('\n'))

        return el


class TextPattern(TextPatternBase):
    """
    A markdown extension for including complete source code files.
    """
    RE = r'^!text\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, **kwargs):
        super(TextPattern, self).__init__(self.RE, **kwargs)

        # Add to the default settings
        self._settings['line'] =  None
        self._settings['start'] =  None
        self._settings['end'] =  None
        self._settings['include_end'] = False

    def handleMatch(self, match):
        """
        Process the text file provided.
        """

        # Update the settings from regex match
        settings = self.getSettings(match.group(3))

        # Read the file
        rel_filename = match.group(2).lstrip('/')
        filename = MooseDocs.abspath(rel_filename)
        if not os.path.exists(filename):
            return self.createErrorElement("Unable to locate file: {}".format(rel_filename))
        if settings['line']:
            content = self.extractLine(filename, settings["line"])

        elif settings['start'] or settings['end']:
            content = self.extractLineRange(filename, settings['start'], settings['end'], settings['include_end'])

        else:
            with open(filename) as fid:
                content = fid.read()

        if content == None:
            return self.createErrorElement("Failed to extract content from {}.".format(filename))

        # Return the Element object
        el = self.createElement(match.group(2), content, filename, rel_filename, settings)
        return el

    def extractLine(self, filename, desired):
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

    def extractLineRange(self, filename, start, end, include_end):
        """
        Function for extracting content between start/end strings.

        Args:
          filename[str]: The name of the file to examine.
          start[str|None]: The starting line (when None is provided the beginning is used).
          end[str|None]: The ending line (when None is provided the end is used).
          include_end[bool]: If True then the end string is included
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


class InputPattern(TextPatternBase):
    """
    Markdown extension for extracting blocks from input files.
    """

    CPP_RE = r'^!input\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, **kwargs):
        TextPatternBase.__init__(self, self.CPP_RE, language='text', **kwargs)
        self._settings['block'] = None

    def handleMatch(self, match):
        """
        Process the input file supplied.
        """

        # Update the settings from regex match
        settings = self.getSettings(match.group(3))

        # Build the complete filename.
        rel_filename = match.group(2)
        filename = MooseDocs.abspath(rel_filename)

        # Read the file and create element
        if not os.path.exists(filename):
            el = self.createErrorElement("The input file was not located: {}".format(rel_filename))
        elif settings['block'] is None:
            el = self.createErrorElement("Use of !input syntax while not providing a block=some_block. If you wish to include the entire file, use !text instead")
        else:
            parser = ParseGetPot(filename)
            node = parser.root_node.getNode(settings['block'])

            if node == None:
                el = self.createErrorElement('Failed to find {} in {}.'.format(settings['block'], rel_filename))
            else:
                content = node.createString()
                label = match.group(2) if match.group(2) else rel_filename
                el = self.createElement(label, content, filename, rel_filename, settings)

        return el


class ClangPattern(TextPatternBase):
    """
    A markdown extension for including source code snippets using clang python bindings.

    Inputs:
      make_dir[str]: (required) The MOOSE application directory for running make command.
      **kwargs: key, value arguments passed to base class.
    """

    # REGEX for finding: !clang /path/to/file.C|h method=some_method
    CPP_RE = r'^!clang\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, **kwargs):
        super(ClangPattern, self).__init__(self.CPP_RE, language='cpp', **kwargs)
        self._settings['method'] = None

        # The make command to execute
        self._make_dir = MooseDocs.abspath(kwargs.pop('make_dir'))
        if not os.path.exists(os.path.join(self._make_dir, 'Makefile')):
            log.error("Invalid path provided for make: {}".format(self._make_dir))
            raise Exception('Critical Error')

    def handleMatch(self, match):
        """
        Process the C++ file provided using clang.
        """
        # Update the settings from regex match
        settings = self.getSettings(match.group(3))

        # Extract relative filename
        rel_filename = match.group(2).lstrip('/')

        # Error if the clang parser did not load
        if not HAVE_MOOSE_CPP_PARSER:
            log.error("Unable to load the MOOSE clang C++ parser.")
            el = self.createErrorElement("Failed to load python clang python bindings.")
            return el

        # Read the file and create element
        filename = MooseDocs.abspath(rel_filename)
        if not os.path.exists(filename):
            el = self.createErrorElement("C++ file not found: {}".format(rel_filename))

        elif settings['method'] is None:
            el = self.createErrorElement("Use of !clang syntax while not providing a method=some_method. If you wish to include the entire file, use !text instead.")

        else:
            log.debug('Parsing method "{}" from {}'.format(settings['method'], filename))

            try:
                parser = mooseutils.MooseSourceParser(self._make_dir)
                parser.parse(filename)
                decl, defn = parser.method(settings['method'])
                el = self.createElement(match.group(2), defn, filename, rel_filename, settings)
            except:
                el = self.createErrorElement('Failed to parse method using clang, check that the supplied method name exists.')

        # Return the Element object
        return el
