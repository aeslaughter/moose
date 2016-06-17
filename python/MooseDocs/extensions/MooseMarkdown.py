import os
import markdown

from MooseInputBlock import MooseInputBlock
from MooseInputFile import MooseInputFile
from MooseCppMethod import MooseCppMethod
from MooseCppFile import MooseCppFile
from MooseSlideTreeprocessor import MooseSlideTreeprocessor

import MooseDocs
import utils


class MooseMarkdown(markdown.Extension):

    def __init__(self, *args, **kwargs):
        #default = {'root': '..', 'repo':None}
        self.config = {'source': [[None], "The source directories to utilize when searching for files."]}

        super(MooseMarkdown, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):

        src = self.config['source'][0]
        print src
        #md.treeprocessors.add('moose_slides', MooseSlideTreeprocessor(md), '_end')
        #md.inlinePatterns.add('moose_input_block', MooseInputBlock(), '<image_link')
        #md.inlinePatterns.add('moose_input_file', MooseInputFile(), '<image_link')
        md.inlinePatterns.add('moose_cpp_method', MooseCppMethod(src), '<image_link')
        #md.inlinePatterns.add('moose_cpp_file', MooseCppFile(), '<image_link')


def makeExtension(*args, **kwargs):
    return MooseMarkdown(*args, **kwargs)

if __name__ == '__main__':

    md = markdown.Markdown(extensions=[makeExtension(root='/wrong/dir')])
    md.convertFile(output='test.html',
                   input='/Users/slauae/projects/moose-doc/docs/documentation/MooseFlavoredMarkdown.md')
