import os
import markdown

from MooseMethodSourcePattern import MooseMethodSourcePattern
from MooseCompleteSourcePattern import MooseCompleteSourcePattern
from MooseSlideTreeprocessor import MooseSlideTreeprocessor

import MooseDocs
import utils




class MooseMarkdown(markdown.Extension):

    def __init__(self, parser, *args, **kwargs):
        super(MooseMarkdown, self).__init__(*args, **kwargs)

        self._parser = parser

    def extendMarkdown(self, md, md_globals):

        #TOD0: Make this a configure option or something generic?
        #path = os.path.join(MooseDocs.MOOSE_DIR, 'framework')
        #print utils.colorText('{} {}'.format('Building Include List:', path), 'YELLOW')
        #parser = utils.MooseSourceParser(path)

        #md.treeprocessors.add('moose_slides', MooseSlideTreeprocessor(md), '_end')
        md.inlinePatterns.add('moose_method_source', MooseMethodSourcePattern(self._parser), '<image_link')
        md.inlinePatterns.add('moose_complete_source', MooseCompleteSourcePattern(), '<image_link')


def makeExtension(*args, **kwargs):

    #TODO: Make this a configure option or something generic?
    path = os.path.join(MooseDocs.MOOSE_DIR, 'framework')
    print utils.colorText('{} {}'.format('Building Include List:', path), 'YELLOW')
    parser = utils.MooseSourceParser(path)

    return MooseMarkdown(parser, *args, **kwargs)

if __name__ == '__main__':

    md = markdown.Markdown(extensions=[MooseMarkdown()])
    md.convertFile(output='test.html',
                   input='/Users/slauae/projects/moose-doc/docs/documentation/MooseFlavoredMarkdown.md')
