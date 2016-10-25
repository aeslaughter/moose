import os
import sys
import markdown
import markdown_include
import bs4
import shutil
import jinja2
import logging
log = logging.getLogger(__name__)

import MooseDocs
from NavigationNode import NavigationNode
from MoosePage import MoosePage

def build_options(parser, subparser):
  """
  Command-line options for build command.
  """
  build_parser = subparser.add_parser('build', help='Generate and Build the documentation for serving.')
  return build_parser


def make_tree(pages, node):
  for p in pages:
    for k, v in p.iteritems():
      if isinstance(v, list):
        child = NavigationNode(name=k, parent=node)
        node.children.append(child)
        make_tree(v, child)
      else:
        page = MoosePage(name=k, parent=node, markdown=v, parser=parser)
        node.children.append(page)


def flat(node):
  for child in node.children:
    if isinstance(child, MoosePage):
      yield child
    for c in flat(child):
      yield c


def copy_files(source, destination, extensions=[]):
  """
  A helper function for copying files
  """

  for root, dirs, files in os.walk(source):
    for filename in files:

      # Only examine files with the supplied extensions
      _, ext = os.path.splitext(filename)
      if ext not in extensions:
        continue

      # Define the complete source and destination filenames
      src = os.path.join(root, filename)
      dst = os.path.join(destination, filename)

      # Update the file, if it is out-of-date
      if (not os.path.exists(dst)) or (os.path.getmtime(src) > os.path.getmtime(dst)):
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
          log.debug('Creating {} directory.'.format(destination))
          os.makedirs(dst_dir)
        log.debug('Copying file {} --> {}'.format(src, dst))
        shutil.copy(src, dst)



def build(config_file='moosedocs.yml', **kwargs):#, live_server=False, pages='pages.yml', page_keys=[], clean_site_dir=False, **kwargs):
  """
  Build the documentation using mkdocs build command.

  Args:
    config_file[str]: (Default: 'mkdocs.yml') The configure file to pass to mkdocs.
  """


  config = MooseDocs.yaml_load(config_file)
  pages = MooseDocs.load_pages(config['pages'])

  copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js'), os.path.join(config['site_dir'], 'js'), extensions=['.js'])
  copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css'), os.path.join(config['site_dir'], 'css'), extensions=['.css'])


  # TODO: Update this to use list provide in configuration
  md_config = config['markdown_extensions'][-1]['MooseDocs.extensions.MooseMarkdown']

  moose = MooseDocs.extensions.MooseMarkdown(**md_config)
  parser = markdown.Markdown(extensions=[moose, 'markdown_include.include', 'admonition', 'mdx_math', 'toc', 'extra'])



  # Create the
  tree = NavigationNode(name='root')
  make_tree(pages, tree)

  all_pages = list(flat(tree))



  def create(i):

    page = all_pages[i]

    page.parse()

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    env.filters['isActive']=page.isActive
    template = env.get_template(config['template'])


    complete = template.render(current=page, tree=tree, javascript=config['extra_javascript'], stylesheets=config['extra_css'])

    destination = config['site_dir']
    if not os.path.exists(destination):
      os.makedirs(destination)

    index = os.path.join(destination, 'index.html')
    with open(index, 'w') as fid:
      log.info('Creating {}'.format(index))
      soup = bs4.BeautifulSoup(complete, 'html.parser')
      fid.write(soup.prettify().encode('utf-8'))


  import multiprocessing
  p = multiprocessing.Pool(multiprocessing.cpu_count())
  p.map(create, range(len(all_pages)))


  copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'media'), os.path.join(config['site_dir'], 'media'), extensions=['.png', '.svg'])


  return config
