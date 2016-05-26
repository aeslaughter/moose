import MooseDocs

import markdown
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import os
import re

class MooseCompleteSourcePattern(Pattern):

    CPP_RE = r'!\[(.*?)\]\((.*\.[Ch])\)'

    def __init__(self):
        Pattern.__init__(self, self.CPP_RE)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Build the complete filename.
        # NOTE: os.path.join doesn't like the unicode even if you call str() on it first.
        filename = MooseDocs.MOOSE_DIR.rstrip('/') + os.path.sep + match.group(3).lstrip('/')

        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('font')
            el.set('color', 'red')
            el.text = 'ERROR: Invalid filename: ' + filename
            return el

        # Read the file
        fid = open(filename)
        content = fid.read()
        fid.close()

        # Strip header and leading/trailing whitespace and newlines
        strt = content.find('/********')
        stop = content.rfind('*******/\n')
        content = content.replace(content[strt:stop+9], '')
        content = re.sub(r'^(\n*)', '', content)
        content = re.sub(r'(\n*)$', '', content)

        # Build the Element object
        el = etree.Element('pre')
        label = etree.SubElement(el, 'p')
        label.text = match.group(1)
        code = etree.SubElement(el, 'code')
        code.set('class', 'c++')
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
        md.inlinePatterns.add('moose_complete_source', MooseCompleteSourcePattern(), '_begin')


def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':

    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(output='test.html',
                   input='/Users/slauae/projects/moose/docs/documentation/MooseFlavoredMarkdown.md')
