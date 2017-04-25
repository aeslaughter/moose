import markdown
import bs4
from markdown.postprocessors import Postprocessor
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
        md.postprocessors.add('moose_code_button', CopyPostprocessor(markdown_instance=md, **config), '_end')
        md.postprocessors.add('moose_content_scroll', ScrollPostprocessor(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs):
    return MiscExtension(*args, **kwargs)


class CopyPostprocessor(Postprocessor):
    """
    Adds "copy" button to code blocks and corrects the language class for working with Prism.js
    """

    def __init__(self, markdown_instance=None, **kwargs):
        super(CopyPostprocessor, self).__init__(markdown_instance)

    def run(self, text):
        """
        Search the tree for <pre><code> blocks and add copy button.
        """
        count = 0
        soup = bs4.BeautifulSoup(text, 'lxml')
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if pre and code:
                lang = code.get('class', 'text')
                pre['class'] = 'language-{}'.format(lang)

                id_ = code.get('id', 'moose-code-block-{}'.format(count))
                code['id'] = id_

                btn = soup.new_tag('button')
                btn['class'] = 'moose-copy-button btn'
                btn['data-clipboard-target'] = '#{}'.format(id_)
                btn.string = 'copy'

                pre.insert(0, btn)
                count += 1
        return unicode(soup)


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
        content = soup.find('div', id='moose-markdown-content')
        if content is None:
            return text

        for h in content.find_all('h2'):
            div = soup.new_tag('div')
            div['class'] = 'section scrollspy'
            h.insert_before(div)
            for sibling in h.next_siblings:
                if sibling.name == 'h2':
                    break
                div.append(sibling.extract())
            div.insert(0, h.extract())
        return unicode(soup)
