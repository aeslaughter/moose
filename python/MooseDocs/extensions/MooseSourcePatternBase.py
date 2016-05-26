import re
import os
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import MooseDocs

class MooseSourcePatternBase(Pattern):
    """
    Base class for pattern matching source code blocks.

    Args:
        regex: The string containing the regular expression to match.
    """

    def __init__(self, regex):
        Pattern.__init__(self, regex)
        #super(Pattern, self).__init__(regex) # This fails

        # The default settings
        self._settings = {'strip_header':True,
                          'github_link':True,
                          'overflow-y':'visible',
                          'max-height':'500px',
                          'strip-extra-newlines':False}

    def updateSettings(self, settings):
        """
        Apply the settings captured from the regular expression.

        Args:
            settings[str]: A string containing the space separate key, value pairs (key=value key2=value2).
        """
        for s in settings.split(' '):
            if s:
                k, v = s.strip().split('=')
                if k not in self._settings:
                    #@TODO: Log this
                    print 'Unknown setting', k
                    continue
                try:
                    self._settings[k] = eval(v)
                except:
                    self._settings[k] = str(v)


    def style(self, *keys):
        """
        Extract the html style string from a list of settings.

        Args:
            *keys[str]: A list of keys to compose into a style string.
        """
        style = []
        for k in keys:
            style.append('{}:{}'.format(k, self._settings[k]))
        return ';'.join(style)

    def createElement(self, label, content, filename, rel_filename):
        """
        Create the code element from the supplied source code content.

        Args:
            label[str]: The label supplied in the regex, [label](...)
            content[str]: The code content to insert into the markdown.
            filename[str]: The complete filename (for error checking)
            rel_filename[str]: The relative filename; used for creating github link.

        NOTE: The code related settings and clean up are applied in this method.
        """

        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('p')
            el.set('style', "color:red;font-size:150%")
            el.text = 'ERROR: Invalid filename: ' + filename
            return el

        # Strip header and leading/trailing whitespace and newlines
        if self._settings['strip_header']:
            strt = content.find('/********')
            stop = content.rfind('*******/\n')
            content = content.replace(content[strt:stop+9], '')
        content = re.sub(r'^(\n*)', '', content)
        content = re.sub(r'(\n*)$', '', content)

        if self._settings['strip-extra-newlines']:
            content = re.sub(r'(\n{3,})', '\n\n', content)

        # Build outer div container
        el = etree.Element('div')

        # Build label
        if self._settings['github_link']:
            label = etree.SubElement(el, 'a')
            label.set('href', MooseDocs.MOOSE_REPOSITORY.rstrip('/') + os.path.sep + rel_filename)
        else:
            label = etree.SubElement(el, 'div')
        label.text = label

        # Build the code
        pre = etree.SubElement(el, 'pre')
        code = etree.SubElement(pre, 'code')
        code.set('class', 'c++')
        code.set('style', self.style('overflow-y', 'max-height'))
        code.text = content

        return el
