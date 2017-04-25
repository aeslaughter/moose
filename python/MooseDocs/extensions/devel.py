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
        md.inlinePatterns.add('moose_extension_config', ExtensionConfigPattern(markdown_instance=md, **config), '_begin')
        md.inlinePatterns.add('moose_extension_component_settings', ExtensionSettingsPattern(markdown_instance=md, **config), '_begin')

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
        url = match.group(2)

        # A tuple separating specific MOOSE documentation features from HTML styles
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

    RE = r'!moosepackage\s*(.*?)!'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['arch'] = (None, "The architecture to return (e.g., osx10.12)")
        settings['return'] = (None, "The information to return ('link' or 'name')")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

        # Load the yaml data containing package information
        self.package = MooseDocs.yaml_load(kwargs.pop('package_file'))

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


class ExtensionConfigPattern(MooseCommonExtension, Pattern):
    """
    Extension for display MarkdownExtension config options in a table.
    """
    RE = r'^!extension\s+(.*?)\s*(?:$|\s+)(.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['title'] = ('Extension Configuration Options', "The title to place above the generated table (title=None removes the heading)")
        settings['title-level'] = ('h2', "The HTML level for the generated title.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

    def handleMatch(self, match):
        """
        Creates table of extension configuration options.
        """
        extensions = [obj.__class__.__name__ for obj in self.markdown.registeredExtensions]
        name = str(match.group(2))
        settings = self.getSettings(match.group(3))

        if name not in extensions:
            return self.createErrorElement('Unknown extension name: {}'.format(name))

        ext = self.markdown.registeredExtensions[extensions.index(name)]
        table = MooseDocs.MarkdownTable('Name', 'Default', 'Description')
        for key, value in ext.config.iteritems():
            table.addRow(key, repr(value[0]), value[1])

        if table:
            div = self.applyElementSettings(etree.Element('div'), settings)
            if settings['title']:
                h = etree.SubElement(div, settings['title-level'])
                h.text = settings['title']
            div.append(table.html())
            return div
        return etree.Element('div') # return an empty div if no configuration options are available

class ExtensionSettingsPattern(MooseCommonExtension, Pattern):
    """
    Provides a table for the MooseCommonExtension settings.
    """
    RE = r'^!extension-settings\s+(.*?)\s*(?:$|\s+)(.*)'

    @staticmethod
    def defaultSettings():
        settings = MooseCommonExtension.defaultSettings()
        settings['title'] = ('Extension Command Settings', "The title to place above the generated table (title=None removes the heading)")
        settings['title-level'] = ('h3', "The HTML level for the generated title.")
        return settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Pattern.__init__(self, self.RE, markdown_instance)

    def handleMatch(self, match):
        """
        Creates table of MooseCommonExtension settings.
        """
        name = str(match.group(2))
        settings = self.getSettings(match.group(3))

        obj = self.find(name)
        if obj is None:
            return self.createErrorElement('Unknown extension module: {}'.format(name))
        elif not isinstance(obj, MooseCommonExtension):
            return self.createErrorElement('The extension module must be a "{}" object, but a "{}" was found.'.format(MooseCommonExtension.__name__, type(obj).__name__))

        table = MooseDocs.MarkdownTable('Name', 'Default', 'Description')
        for key, value in obj.defaultSettings().iteritems():
            table.addRow(key, repr(value[0]), value[1])

        if table:
            div = self.applyElementSettings(etree.Element('div'), settings)
            if settings['title']:
                h = etree.SubElement(div, settings['title-level'])
                h.text = settings['title']

            div.append(table.html())
            return div
        return etree.Element('div') # return an empty div if no settings are available

    def find(self, name):
        """
        Locate the extension component with the markdown object.
        """
        containers = [self.markdown.preprocessors,
                      self.markdown.inlinePatterns,
                      self.markdown.treeprocessors,
                      self.markdown.postprocessors,
                      self.markdown.parser.blockprocessors]
        for container in containers:
            if name in container:
                return container[name]
        return None
