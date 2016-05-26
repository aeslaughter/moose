import os
import re
import markdown
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree

from MooseSourcePatternBase import MooseSourcePatternBase
import MooseDocs
import utils


class MooseCompleteSourcePattern(MooseSourcePatternBase):
    """
    A markdown extension for including complete source code files.
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Chi])\s*(.*?)\)'

    def __init__(self):
        super(MooseCompleteSourcePattern, self).__init__(self.CPP_RE)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Update the settings from regex match
        self.updateSettings(match.group(4))

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        rel_filename = match.group(3).lstrip('/')
        filename = MooseDocs.MOOSE_DIR.rstrip('/') + os.path.sep + rel_filename

        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('p')
            el.set('style', "color:red;font-size:150%")
            el.text = 'ERROR: Invalid filename: ' + filename
            return el

        # Read the file
        fid = open(filename)
        content = fid.read()
        fid.close()

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
        label.text = match.group(2)

        # Build the code
        pre = etree.SubElement(el, 'pre')
        code = etree.SubElement(pre, 'code')
        code.set('class', 'c++')
        code.set('style', self.style('overflow-y', 'max-height'))
        code.text = content

        return el


class MooseSlideTreeprocessor(Preprocessor):
    def __init(self, *args):
        pass

    def run(self, root):

        new_root = etree.Element('div')
        section = etree.SubElement(new_root, 'section')

        for child in root:
            if child.text == u'!---':
                section = etree.SubElement(new_root, 'section')
            else:
                new = etree.SubElement(section, child.tag)
                new.append(child)

        return new_root

class MooseMarkdown(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        #md.treeprocessors.add('moose_slides', MooseSlideTreeprocessor(md), '_end')
        md.inlinePatterns.add('moose_complete_source', MooseCompleteSourcePattern(), '<image_link')


def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':

    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(output='test.html',
                   input='/Users/slauae/projects/moose/docs/documentation/MooseFlavoredMarkdown.md')
