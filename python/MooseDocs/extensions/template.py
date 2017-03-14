import os
import copy
import jinja2
import bs4
import shutil
import markdown
from markdown.postprocessors import Postprocessor
import logging
log = logging.getLogger(__name__)
import MooseDocs

class TemplateExtension(markdown.Extension):
    """
    Extension for applying template to converted markdown.
    """

    def __init__(self, **kwargs):
        self.config = dict()
        self.config['template'] = ['', "The jinja2 template to apply."]
        self.config['template_args'] = [dict(), "Arguments passed to to the MooseTemplate Postprocessor."]
        self.config['environment_args'] = [dict(), "Arguments passed to the jinja2.Environment."]
        super(TemplateExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Applies template to html converted from markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.postprocessors.add('moose_template', TemplatePostprocessor(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs):
    return TemplateExtension(*args, **kwargs)

class TemplatePostprocessor(Postprocessor):
    """
    Extension for applying converted html content to an jinja2 template.
    """
    def __init__(self, markdown_instance, **config):
        super(TemplatePostprocessor, self).__init__(markdown_instance)
        self._template = config.pop('template')
        self._template_args = config.pop('template_args', dict())
        self._environment_args = config.pop('environment_args', dict())

    def globals(self, env):
        """
        Defines global template functions.
        """
        env.globals['insert_files'] = self._insertFiles

    def run(self, text):
        """
        Apply the converted text to an jinja2 template and return the result.
        """
        # Update the meta data to proper python types
        meta = dict()
        for key, value in self.markdown.Meta.iteritems():
            meta[key] = eval(''.join(value))

        # Define template arguments
        template_args = copy.copy(self._template_args)
        template_args.update(meta)
        template_args['content'] = text
        template_args['tableofcontents'] = self._tableofcontents(text)
        if 'navigation' in template_args:
            template_args['navigation'] = MooseDocs.yaml_load(MooseDocs.abspath(template_args['navigation']))

        # Execute template and return result
        paths = [os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'templates'), os.path.join(os.getcwd(), 'templates')]
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(paths), **self._environment_args)
        self.globals(env)
        template = env.get_template(self._template)
        complete = template.render(current=self.markdown.current, **template_args)

        # Finalize the contents for output
        soup = bs4.BeautifulSoup(complete, 'html.parser')
        self._imageLinks(self.markdown.current, soup)
        self._markdownLinks(self.markdown.current, soup)
        self._contentSections(self.markdown.current, soup)
        return soup.prettify()

    @staticmethod
    def _insertFiles(filenames):
        """
        Helper function for jinja2 to read css file and return as string.
        """
        if isinstance(filenames, str):
            filenames = [filenames]

        for filename in filenames:
            with open(MooseDocs.abspath(filename), 'r') as fid:
                return fid.read().strip('\n')

    @staticmethod
    def _imageLinks(node, soup):
        """
        Makes images links relative
        """
        for img in soup('img'):
            img['src'] = node.relpath(img['src'])

    def _markdownLinks(self, node, soup):
        """
        Performs auto linking of markdown files.
        """
        def finder(node, desired, pages):
            """
            Locate nodes for the 'desired' filename
            """
            if node.source() and node.source().endswith(desired):
                pages.append(node)
            for child in node:
                finder(child, desired, pages)
            return pages

        # Loop over <a> tags and update links containing .md to point to .html
        for link in soup('a'):
            href = link.get('href')
            if href and (not href.startswith('http')) and href.endswith('.md'):
                found = []
                finder(node.root(), href, found)

                # Error if file not found or if multiple files found
                if not found:
                    #TODO: convert to error when MOOSE is clean
                    log.warning('Failed to locate page for markdown file {} in {}'.format(href, node.source()))
                    link['class'] = 'moose-bad-link'
                    continue

                elif len(found) > 1:
                    msg = 'Found multiple pages matching the supplied markdown file {} in {}:'.format(href, node.source())
                    for f in found:
                        msg += '\n    {}'.format(f.source())
                    log.error(msg)

                # Update the link with the located page
                url = node.relpath(found[0].url())
                #log.debug('Converting link: {} --> {}'.format(href, url))
                link['href'] = url

    @staticmethod
    def _contentSections(node, soup):
        """
        Add div sections for scrollspy to work correctly with materialize.
        """
        # Add materialize sections for table-of-contents
        div = soup.find('div', id='moose-markdown-content')
        if div:
            current = div
            for tag in div.contents:
                if isinstance(tag, bs4.element.Tag):
                    if tag.name == 'h2':
                        current = soup.new_tag('div', id=tag.get('id', '#'))
                        current.attrs['class'] = "section scrollspy"

                    if current != tag.parent:
                        tag.wrap(current)

    @staticmethod
    def _tableofcontents(text, level='h2'):
        soup = bs4.BeautifulSoup(text, 'html.parser')
        for tag in soup.find_all(level):
            if 'id' in tag.attrs:
                yield (tag.contents[0], tag.attrs['id'])
