"""
Markdown for developer information: buildstatus and package data.
"""
import os
from markdown.util import etree
from markdown.util import AtomicString
import logging
log = logging.getLogger(__name__)

import markdown
from markdown.inlinepatterns import Pattern
from MooseCommonExtension import MooseCommonExtension
import MooseDocs

class DevelExtension(markdown.Extension):
    """
    Extension for adding developer tools to MOOSE flavored markdown.xk
    """

    def __init__(self, **kwargs):
        self.config = dict()
        default = os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'packages.yml')
        self.config['package_file'] = [default, "The 'package.yml' configuration file."]
        super(DevelExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds developer tools to MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.inlinePatterns.add('moose_build_status', BuildStatusPattern(markdown_instance=md, **config), '_begin')
        md.inlinePatterns.add('moose_package_parser', PackagePattern(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs):
    return DevelExtension(*args, **kwargs)


class BuildStatusPattern(MooseCommonExtension, Pattern):
    """
    Markdown extension for add Build Status widget.

    Usage:
     !buildstatus http://civet/buildstatus/site css_attribute=setting

    """

    # Find !buildstatus url attribute=value
    RE = r'^!buildstatus\s+(.*?)(?:$|\s+)(.*)'

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

    def handleMatch(self, match):
        """
        process settings associated with !buildstatus markdown
        """
        reverse_margin = { 'left' : 'right',
                           'right' : 'left',
                           'None' : 'none'}

        url = match.group(2)

        # A tuple separating specific MOOSE documentation features (self._settings) from HTML styles
        settings = self.getSettings(match.group(3))

        # Create parent div, and set any allowed CSS
        parent_div = self.applyElementSettings(etree.Element('div'), settings)
        parent_div.set('class', 'moose-buildstatus')

        child_div = etree.SubElement(parent_div, 'div')
        jquery_script = etree.SubElement(parent_div, 'script')
        build_status_script = etree.SubElement(parent_div, 'script')

        jquery_script.set('src', 'http://code.jquery.com/jquery-1.11.0.min.js')

        # We need to inform SmartyPants to not format for paragraph use
        build_status_script.text = AtomicString('$(document).ready(function(){ $("#buildstatus").load("%s");});' % (url))

        # Set some necessary defaults for our child div
        child_div.set('id', 'buildstatus')

        # Set any additional allowed CSS
        return parent_div


class PackagePattern(MooseCommonExtension, Pattern):
    """
    Markdown extension for extracting package arch and version.
    """

    RE = r'!MOOSEPACKAGE\s*(.*?)!'

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

        # Load the yaml data containing package information
        self.package = MooseDocs.yaml_load(kwargs.pop('package_file'))

        # The default settings
        self._settings['arch'] = None
        self._settings['return'] =  None

    def handleMatch(self, match):
        """
        Returns a tree element package information.
        """
        # Update the settings from regex match
        settings = self.getSettings(match.group(2))
        if not settings.has_key('arch') or not settings.has_key('return'):
            el = self.createErrorElement('Invalid MOOSEPACKAGE markdown syntax. Requires arch=, return=link|name')
        else:
            if settings['arch'] not in self.package.keys():
                el = self.createErrorElement('"arch" not found in packages.yml')
            else:
                if settings['return'] == 'link':
                    el = etree.Element('a')
                    el.set('href', self.package['link'] + self.package[settings['arch']]['name'])
                    el.text = self.package[settings['arch']]['name']
                elif settings['return'] == 'name':
                    el = etree.Element('p')
                    el.text = self.package[settings['arch']]['name']
        return el
