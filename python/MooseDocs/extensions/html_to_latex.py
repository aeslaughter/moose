import markdown

from markdown.postprocessors import Postprocessor

import MooseDocs
from MooseDocs.html2latex import Translator
from MooseDocs.html2latex import BasicExtension
from MooseDocs.html2latex import MooseExtension



class HTML2LatexExtension(markdown.Extension):

    def __init__(self, **kwargs):
        self.config = dict()
        self.config['site'] = ['', "The website for where markdown links should be connected in latex/pdf file."]
        self.config['hrule'] = [False, "Enable/disable the use use of \hrule in generated latex."]
        self.config['headings'] = [['section', 'subsection', 'subsubsection', 'textbf', 'underline', 'emph'], "The latex commands for the h1, h2, h3, h4, h5, and h6 tags for the document, all must be supplied and only commands valid in the latex body are allowed."]
        super(HTML2LatexExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        config = self.getConfigs()

        loc = '<moose_template' if 'moose_template' in md.postprocessors else '_end'
        md.postprocessors.add('moose_latex', LatexPostprocessor(markdown_instance=md, **config), loc)


def makeExtension(*args, **kwargs):
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
