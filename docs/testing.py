import os
import sys
import collections
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


class MoosePage(object):

    def __init__(self, filename, markdown=None, root='', breadcrumbs=[]):

        self._markdown = markdown
        self._breadcrumbs = breadcrumbs
        self._filename = filename
        self._root = root
        self._html = None


        local = os.path.join(*self._breadcrumbs).lower().replace(' ', '_')
        self._url = os.path.join(local, 'index.html')
        self._full = os.path.join(self._root, self._url)

    def initialize(self, breadcrumbs=[]):
        pass

    def isActive(self, tree):

        def helper(tree):
            for key, value in tree.iteritems():
                if isinstance(value, collections.OrderedDict):
                    for h in helper(value):
                        yield h

                else:
                    yield self == value

        if any(helper(tree)):
            return " active"
        else:
            return ''


    def breadcrumbs(self):
        """

        """
        return []

        #TODO: This doesn't work b/c the html has not been created. This needs to be handled
        # in another way, perhaps by inspecting the tree
        """
        output = []
        for i, crumb in enumerate(self._breadcrumbs):
            local = os.path.join(*self._breadcrumbs[0:i+1]).lower().replace(' ', '_')
            #local = os.path.join(self._root, local)
            index = os.path.join(local, 'index.html')
            overview = os.path.join(local, 'overview', 'index.html')

            if os.path.exists(index):
                output.append((crumb, index))
            elif os.path.exists(overview):
                output.append((crumb, overview))
            else:
                output.append((crumb, None))

        return output
        """

    def __eq__(self, other):
      return self._breadcrumbs == other._breadcrumbs and self._filename == other._filename

    def url(self):
        return self._url

    def dirname(self):
        return os.path.dirname(self._full)

    def html(self):
        return self._html

    def parse(self):

        with open(self._filename, 'r') as fid:
            md = fid.read()

        self._html = parser.convert(md.decode('utf-8'))


def make_dict(node, sitemap=collections.OrderedDict(), crumbs=['']*100, root='', level=0):
    for n in node:
        for k, v in n.iteritems():
            crumbs[level] = k
            if k not in sitemap:
                sitemap[k] = collections.OrderedDict()
            if isinstance(v, list):
                make_dict(v, sitemap=sitemap[k], crumbs=crumbs, root=root, level=level+1)
            else:
                page = MoosePage(v, breadcrumbs=crumbs[0:level+1], root=root, markdown=parser)
                sitemap[k] = page

def flat(node):
    for k, v in node.iteritems():
        if isinstance(v, collections.OrderedDict):
            for page in flat(v):
                yield page
        else:
            yield  v









sitemap = collections.OrderedDict()
make_dict(pages, sitemap=sitemap, root=root)

all_pages = flat(sitemap)

for page in all_pages:

    page.parse()

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    env.filters['isActive']=page.isActive
    template = env.get_template('materialize.html')


    complete = template.render(content=page.html(), breadcrumbs=page.breadcrumbs(),
                               sitemap=sitemap, url=page.url(), current=page)

    destination = page.dirname()
    if not os.path.exists(destination):
        os.makedirs(destination)

    index = os.path.join(destination, 'index.html')
    with open(index, 'w') as fid:
        print index
        soup = bs4.BeautifulSoup(complete, 'html.parser')
        fid.write(soup.prettify().encode('utf-8'))
