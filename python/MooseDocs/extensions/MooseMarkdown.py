import MooseDocs

import markdown
from markdown.inlinepatterns import Pattern
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import os
import re

class MooseCompleteSourcePattern(Pattern):
    """


    strip_header:True
    github_link:True
    overflow-y:visible
    max-height:None
    """

    CPP_RE = r'!\[(.*?)\]\((.*\.[Chi])\s*(.*?)\)'


    def __init__(self):
        Pattern.__init__(self, self.CPP_RE)

    def handleMatch(self, match):
        """
        Process the C++ file provided.
        """

        # Current settings
        settings = {'strip_header':True, 'github_link':True, 'overflow-y':'visible', 'max-height':None}
        for s in match.group(4).split(' '):
            if s:
                k, v = s.strip().split(':')
                if k not in settings:
                    #@TODO: Log this
                    print 'Unknown setting', k
                    continue
                try:
                    settings[k] = eval(v)
                except:
                    settings[k] = str(v)

        print settings

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
        if settings['strip_header']:
            strt = content.find('/********')
            stop = content.rfind('*******/\n')
            content = content.replace(content[strt:stop+9], '')
        content = re.sub(r'^(\n*)', '', content)
        content = re.sub(r'(\n*)$', '', content)

        # Build outer div container
        el = etree.Element('div')

        # Build label
        if settings['github_link']:
            label = etree.SubElement(el, 'a')
            label.set('href', MooseDocs.MOOSE_REPOSITORY.rstrip('/') + os.path.sep + rel_filename)
        else:
            label = etree.SubElement(el, 'div')
        label.text = match.group(2)

        # Build the code
        pre = etree.SubElement(el, 'pre')
        code = etree.SubElement(pre, 'code')
        code.set('class', 'c++')
        #code.set('overflow-y', settings['overflow-y'])
        #if settings['max-height']:
        #    code.set('max-height', settings['max-height'])
        code.text = content

        etree.dump(el)
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
