import markdown

from markdown.postprocessors import Postprocessor

import MooseDocs
from MooseDocs.html2latex import Translator
from MooseDocs.html2latex import BasicExtension
from MooseDocs.html2latex import MooseExtension
from MooseMarkdownExtension import MooseMarkdownExtension


class HTML2LatexExtension(MooseMarkdownExtension):

    @staticmethod
    def defaultConfig():
        config = MooseMarkdownExtension.defaultConfig()
        config['site'] = ['', "The website for where markdown links should be connected in latex/pdf file."]
        config['hrule'] = [False, "Enable/disable the use use of \hrule in generated latex."]
        config['headings'] = [['section', 'subsection', 'subsubsection', 'textbf', 'underline', 'emph'], "The latex commands for the h1, h2, h3, h4, h5, and h6 tags for the document, all must be supplied and only commands valid in the latex body are allowed."]
        return config

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        config = self.getConfigs()

        loc = '<moose_template' if 'moose_template' in md.postprocessors else '_end'
        md.postprocessors.add('moose_latex', LatexPostprocessor(markdown_instance=md, **config), loc)


def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
    return HTML2LatexExtension(*args, **kwargs)

class LatexPostprocessor(Postprocessor):
    """
    Extension for converting html to latex.
    """
    def __init__(self, markdown_instance, **kwargs):
        super(LatexPostprocessor, self).__init__(markdown_instance)

        self._config = kwargs

    def run(self, text):

        # Build latex
        h2l = Translator(extensions=[BasicExtension(**self._config), MooseExtension(**self._config)])
        tex = h2l.convert(text)
        return tex
