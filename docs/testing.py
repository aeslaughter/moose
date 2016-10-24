import os
import sys
import collections
import shutil
import markdown
import markdown_include
import bs4
from markdown.util import etree

import jinja2

import MooseDocs



root = os.path.join(os.getenv('HOME'), 'projects', 'moose-doc', 'site')

config_file = 'moosedocs.yml'
config = MooseDocs.yaml_load(config_file)
md_config = config['markdown_extensions'][-1]['MooseDocs.extensions.MooseMarkdown']

moose = MooseDocs.extensions.MooseMarkdown(**md_config)
parser = markdown.Markdown(extensions=[moose, 'markdown_include.include', 'admonition', 'mdx_math', 'toc', 'extra'])

pages = MooseDocs.yaml_load('pages.yml')


class NavigationNode(object):
    def __init__(self, name='', parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def __eq__(self, other):
      return self.name == other.name and self.parent == other.parent and self.children == other.children

    def __str__(self):
        return self._string()

    def url(self, **kwargs):

        return None

    def _string(self, level=0):
        output = "{}{}\n".format(' '*2*level, self.name)
        for child in self.children:
            output += child._string(level=level+1)
        return output


class MoosePage(NavigationNode):

    def __init__(self, markdown=markdown, parser=None, root='', **kwargs):
        super(MoosePage, self).__init__(**kwargs)

        self._markdown = markdown


        self._parser = parser
        self._root = root

        self._html = None


        # Populate the list of parent nodes (i.e., "breadcrumbs")
        self._breadcrumbs = []
        def helper(node):
            if node.parent:
                self._breadcrumbs.insert(0, node)
                helper(node.parent)

        helper(self)

        local = [node.name for node in self._breadcrumbs] + ['index.html']
        self._url = os.path.join(*local).lower().replace(' ', '_')

        self._full = os.path.join(self._root, self._url)




        #local = os.path.join(*self._breadcrumbs).lower().replace(' ', '_')
        #self._url = os.path.join(local, 'index.html')

    def _string(self, level):
        return "{}{}: {} {}\n".format(' '*2*level, self.name, self.markdown, list(self._breadcrumbs))

    def isActive(self, tree):

        def helper(tree):
            for child in tree.children:
                for h in helper(child):
                    yield h
                else:
                    yield self == child

        if any(helper(tree)):
            return "active"
        else:
            return ''

    def contents(self, level='h2'):

        soup = bs4.BeautifulSoup(self._html, 'html.parser')
        for tag in soup.find_all(level):
            yield (tag.contents[0], tag.attrs['id'])


    def breadcrumbs(self):
        """

        """
        return self._breadcrumbs

    def url(self, rel=None):
        if rel:
            return os.path.relpath(rel.url(), self._url)
        else:
            return self._url

    def dirname(self):
        return os.path.dirname(self._full)

    def html(self):
        return self._html

    def parse(self):



        with open(self._markdown, 'r') as fid:
            md = fid.read()
        self._html = parser.convert(md.decode('utf-8'))


def make_tree(pages, node, root=''):
    for p in pages:
        for k, v in p.iteritems():
            if isinstance(v, list):
                child = NavigationNode(name=k, parent=node)
                node.children.append(child)
                make_tree(v, child, root=root)
            else:
                page = MoosePage(markdown=v, name=k, root=root, parser=parser, parent=node)
                node.children.append(page)

def flat(node):
    for child in node.children:
        if isinstance(child, MoosePage):
            yield child
        for c in flat(child):
            yield c


tree = NavigationNode(name='root')
make_tree(pages, tree, root=root)

all_pages = list(flat(tree))


def create(i):

    page = all_pages[i]

    page.parse()

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    env.filters['isActive']=page.isActive
    template = env.get_template('materialize.html')


    complete = template.render(current=page, tree=tree)

    destination = page.dirname()
    if not os.path.exists(destination):
        os.makedirs(destination)

    index = os.path.join(destination, 'index.html')
    with open(index, 'w') as fid:
        print index
        soup = bs4.BeautifulSoup(complete, 'html.parser')
        fid.write(soup.prettify().encode('utf-8'))


import multiprocessing
idx =
p = multiprocessing.Pool(multiprocessing.cpu_count())
p.map(create, range(len(all_pages)))

# Copy CSS/js/media
shutil.copy('css/moose.css', '../site/css')
