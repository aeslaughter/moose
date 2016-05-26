import markdown
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import os
import re

MOOSE_DIR = os.getenv('MOOSE_DIR', os.path.join(os.getenv('HOME'), 'projects', 'moose'))

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
        filename = MOOSE_DIR.rstrip('/') + os.path.sep + match.group(3).lstrip('/')

        print match.groups()
        # If the file does not exist return a bold block
        if not os.path.exists(filename):
            el = etree.Element('b')
            el.text = 'ERROR: Invalid filename: ' + filename
            return el

        # Read the file
        fid = open(filename)
        content = fid.read()
        fid.close()

        # Build the Element object
        el = etree.Element('pre')
        code = etree.SubElement(el, 'code')
        code.set('class', 'c++')
        code.text = content
        return el



        """
        parser = MooseClangParser(filename)
        el = etree.Element('pre')
        code = etree.SubElement(el, 'code')
        code.set('class', 'c++')
        code.text = parser.method(match.group(3))
        return el
        """

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
        #print '\n'.join(md.parser.blockprocessors)


        md.treeprocessors.add('moose_slides', MooseSlideTreeprocessor(md), '_end')
        md.inlinePatterns.add('moose_complete_source', MooseCompleteSourcePattern(), '<image_link')




def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':

    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(output='test.html',
                   input='/Users/slauae/projects/moose/docs/documentation/moose_style_markdown.md')
