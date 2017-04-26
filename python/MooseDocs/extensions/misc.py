import markdown
import bs4
from markdown.postprocessors import Postprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree

class MiscExtension(markdown.Extension):
    """
    Extension for adding materialize specific css to converted markdown.
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds materialize specific css to the converted html.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.postprocessors.add('moose_content_scroll', ScrollPostprocessor(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs):
    return MiscExtension(*args, **kwargs)

class ScrollPostprocessor(Postprocessor):
    """
    Adds a 'div' tag around h2 levels with class of 'section scrollspy' to allow scrollable contents
    on right-hand side of pages.
    """

    def __init__(self, markdown_instance=None, **kwargs):
        super(ScrollPostprocessor, self).__init__(markdown_instance)

    def run(self, text):
        """
        Adds section for materialize scrollspy
        """
        soup = bs4.BeautifulSoup(text, 'lxml')
        div = soup.find('div', id='moose-markdown-content')
        if div is None:
            return text

        # Group objects with h2 level headings
        groups = [[]]
        for child in list(div.contents):
            if child.name == 'h2':
                groups.append([])
            groups[-1].append(child)

        # Add groups to wrapping <div> tag
        for group in groups:
            sec = soup.new_tag('div')
            if isinstance(group[0], bs4.Tag):
                sec['id'] = group[0].get('id', '#')
                sec['class'] = 'section scrollspy'
            div.append(sec)
            for tag in group:
                sec.append(tag)

        return unicode(soup)
