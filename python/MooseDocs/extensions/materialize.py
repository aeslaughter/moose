import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree

class MaterializeExtension(markdown.Extension):
    """
    Extension for adding materialize specific css to converted markdown.
    """
    def extendMarkdown(self, md, md_globals):
        """
        Adds materialize specific css to the converted html.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.treeprocessors.add('moose_code_button', CopyTreeprocessor(markdown_instance=md, **config), '_end')
        md.treeprocessors.add('moose_content_scroll', ScrollTreeprocessor(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs):
    return MaterializeExtension(*args, **kwargs)


class CopyTreeprocessor(Treeprocessor):
    """
    Adds "copy" button to code blocks and corrects the language class for working with Prism.js
    """

    def __init__(self, markdown_instance=None, **kwargs):
        super(CopyTreeprocessor, self).__init__(markdown_instance)

    def run(self, root):
        """
        Search the tree for <pre><code> blocks and add copy button.
        """
        count = 0
        for pre in root.iter('pre'):
            code = pre.find('code')
            if code is not None:
                pre.set('class', 'language-{}'.format(code.get('class', 'text')))

                id = code.get('id', 'moose-code-block-{}'.format(count))
                code.set('id', id)

                btn = etree.Element('button')
                btn.set('class', 'moose-copy-button btn')
                btn.set('data-clipboard-target', '#{}'.format(id))
                btn.text = 'copy'

                pre.insert(0, btn)
                count += 1


class ScrollTreeprocessor(Treeprocessor):
    """
    Adds a 'div' tag around h2 levels with class of 'section scrollspy' to allow scrollable contents
    on right-hand side of pages.
    """

    def __init__(self, markdown_instance=None, **kwargs):
        super(ScrollTreeprocessor, self).__init__(markdown_instance)

    def run(self, root):
        """
        Adds section for materialize scrollspy
        """

        div = root.find('div')
        if (div is not None) and (div.get('id', None) == 'moose-markdown-content'):
            current = div
            parent = div
            for el in div.iter():
                if el.name == 'h2':
                    parent = current
                    current = etree.Element('div', id=tag.get('id', '#'))
                    current.set('class', "section scrollspy")

                if current != parent:
                    parent.append(current)
                    current.append(el)
                    parent.remove(el)
