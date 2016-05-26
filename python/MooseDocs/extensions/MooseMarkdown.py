import markdown

from MooseCompleteSourcePattern import MooseCompleteSourcePattern
from MooseSlideTreeprocessor import MooseSlideTreeprocessor


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
