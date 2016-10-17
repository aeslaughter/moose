import os
import collections
import markdown
import markdown_include
import jinja2

import MooseDocs



#pages = MooseDocs.yaml_load('pages.yml')
pages = [MooseDocs.yaml_load('pages.yml')[4]]



class MoosePage(object):

    def __init__(self, filename, breadcrumbs=[], root=''):
        self._breadcrumbs = breadcrumbs
        self._filename = filename
        self._root = root


    def breadcrumbs(self):

        output = collections.OrderedDict()
        for i, crumb in enumerate(self._breadcrumbs):
            local = os.path.join(os.path.join(*self._breadcrumbs[0:i+1]), 'index.html')
            local = local.lower().replace(' ', '_')
            output[crumb] = os.path.join(self._root, local)
        return output

    def destination(self):
        local = os.path.join(*self._breadcrumbs).lower().replace(' ', '_')
        return os.path.join(self._root, local)

    def html(self):
        moose = MooseDocs.extensions.MooseMarkdown()
        parser = markdown.Markdown(extensions=[moose, 'markdown_include.include', 'admonition', 'mdx_math', 'toc', 'extra'])

        with open(self._filename, 'r') as fid:
            md = fid.read()

        return parser.convert(md)




prefix = ['']*600
def flat(node, parent=None, level=0, root=''):
    for n in node:
        for k, v in n.iteritems():
            prefix[level] = k
            if isinstance(v, list):
                for f in flat(v, parent=n, level=level+1, root=root):
                    yield f
            else:
                yield MoosePage(v, breadcrumbs=prefix[0:level] + [k], root=root)


root = os.path.join(os.getenv('HOME'), 'projects', 'moose-doc', 'site')
all_pages = flat(pages, root=root)


for page in all_pages:

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    template = env.get_template('testing.html')


#    for name, link in page.breadcrumbs().iteritems():
#        print name, link

    complete = template.render(content=page.html(), breadcrumbs=page.breadcrumbs())

    destination = page.destination()
    if not os.path.exists(destination):
        os.makedirs(destination)

    index = os.path.join(destination, 'index.html')
    with open(index, 'w') as fid:
        fid.write(complete.encode('utf-8'))
