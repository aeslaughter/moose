import os
import re
import copy
import jinja2
import bs4
import shutil
import markdown
from markdown.postprocessors import Postprocessor
import logging
log = logging.getLogger(__name__)
import MooseDocs
from MooseMarkdownExtension import MooseMarkdownExtension
from app_syntax import AppSyntaxExtension


class TemplateExtension(MooseMarkdownExtension):
    """
    Extension for applying template to converted markdown.
    """
    @staticmethod
    def defaultConfig():
        config = MooseMarkdownExtension.defaultConfig()
        config['template'] = ['', "The jinja2 template to apply."]
        config['template_args'] = [dict(), "Arguments passed to to the MooseTemplate Postprocessor."]
        config['environment_args'] = [dict(), "Arguments passed to the jinja2.Environment."]
        return config

    def extendMarkdown(self, md, md_globals):
        """
        Applies template to html converted from markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()

        md.requireExtension(AppSyntaxExtension)
        ext = md.getExtension(AppSyntaxExtension)
        config['syntax'] = ext.syntax
        md.postprocessors.add('moose_template', TemplatePostprocessor(markdown_instance=md, **config), '_end')

def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
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
        self._syntax = config.pop('syntax')
        self._node = None

    @property
    def node(self):
        self._node = self.markdown.current
        return self._node

    def globals(self, env):
        """
        Defines global template functions.
        """
        env.globals['insert_files'] = self._insertFiles
        env.globals['editMarkdown'] = self._editMarkdown
        env.globals['mooseCode'] = self._code

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
        template_args['doxygen'] = self._doxygen()
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
        return unicode(soup)

    @staticmethod
    def _insertFiles(filenames):
        """
        Helper function for jinja2 to read css file and return as string.
        """
        if isinstance(filenames, str):
            filenames = [filenames]

        out = []
        for filename in filenames:
            with open(MooseDocs.abspath(filename), 'r') as fid:
                out += [fid.read().strip('\n')]
        return '\n'.join(out)

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
            if href and (not href.startswith('http')) and ('.md' in href):

                # Split filename from section link (#)
                parts = href.split('#')

                # Populate the list of found files
                found = []
                finder(node.root(), parts[0], found)

                # Error if file not found or if multiple files found
                if not found:
                    log.error('Failed to locate page for markdown file {} in {}'.format(href, node.source()))
                    link['class'] = 'moose-bad-link'
                    continue

                elif len(found) > 1:
                    msg = 'Found multiple pages matching the supplied markdown file {} in {}:'.format(href, node.source())
                    for f in found:
                        msg += '\n    {}'.format(f.source())
                    log.error(msg)

                # Update the link with the located page
                url = node.relpath(found[0].url())
                if len(parts) == 2:
                    url += '#' + parts[1]
                log.debug('Converting link: {} --> {}'.format(href, url))
                link['href'] = url

    @staticmethod
    def _tableofcontents(text, level='h2'):
        soup = bs4.BeautifulSoup(text, 'html.parser')
        for tag in soup.find_all(level):
            if 'id' in tag.attrs and tag.contents:
                yield (tag.contents[0], tag.attrs['id'])

    def _editMarkdown(self, repo_url):
        """
        Return the url to the markdown file for this object.
        """
        return os.path.join(repo_url, 'edit', 'devel', MooseDocs.relpath(self.node.source()))

    def _doxygen(self):
        # Build a complete list of objects
        for syntax in self._syntax.itervalues():
            for obj in syntax.objects().itervalues():
                if obj.name == self.node.name():
                    return syntax.doxygen(obj.name)

    def _code(self, repo_url):
        """
        Return the GitHub/GitLab addresses for the associated C/h files.

        Args:
          repo_url[str]: Web address to use as the base for creating the edit link
        """
        info = []
        for key, syntax in self._syntax.iteritems():
            for obj in syntax.objects().itervalues():
                if obj.name == self.node.name():
                    info.append(obj)
            for obj in syntax.actions().itervalues():
                if obj.name == self.node.name():
                    info.append(obj)

        output = []
        for obj in info:
            for filename in obj.code:
                rel_filename = MooseDocs.relpath(filename)
                output.append( (os.path.basename(rel_filename), os.path.join(repo_url, 'blob', 'master', rel_filename)) )

        return output
