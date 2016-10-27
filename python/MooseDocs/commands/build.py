import os
import sys
import multiprocessing
import itertools
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


def make_tree(pages, node, parser):
  """
  Create the tree structure of NavigationNode/MoosePage objects
  """
  for p in pages:
    for k, v in p.iteritems():
      if isinstance(v, list):
        child = NavigationNode(name=k, parent=node)
        node.children.append(child)
        make_tree(v, child, parser)
      else:
        page = MoosePage(name=k, parent=node, markdown=v, parser=parser)
        node.children.append(page)


def flat(node):
  """
  Create a flat list of pages for parsing and generation

  Args:
    node[NavigationNode]: The root node to flatten from
  """
  for child in node.children:
    if isinstance(child, MoosePage):
      yield child
    for c in flat(child):
      yield c


def copy_files(**config):
  """
  Copies the js, css, and media files to the site directory.
  """

  def helper(source, destination, extensions=[]):
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
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
          log.debug('Creating {} directory.'.format(destination))
          os.makedirs(dst_dir)

        log.debug('Copying file {} --> {}'.format(src, dst))
        shutil.copy(src, dst)


  site_dir = config['site_dir']
  helper(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js'),
         os.path.join(site_dir, 'js'), extensions=['.js'])
  helper(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css'),
         os.path.join(site_dir, 'css'), extensions=['.css'])
#  copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'fonts'), os.path.join(config['site_dir'], 'fonts'), extensions=['.css'])

  helper(os.path.join(os.getcwd(), 'js'),
         os.path.join(site_dir, 'js'), extensions=['.js'])
  helper(os.path.join(os.getcwd(), 'css'),
         os.path.join(site_dir, 'css'), extensions=['.css'])

  helper(os.path.join(os.getcwd(), 'media'),
         os.path.join(site_dir, 'media'), extensions=['.png', '.svg'])

def relpath(input):
  """
  A utility function for Jinja2 template.

  Args:
    input[tuple]: The os.path.relpath arguments.
  """
  if input[0].startswith('http'):
    return input[0]
  return os.path.relpath(*input)


def build_page(page, tree, config, **kwargs):
  """
  Build the html for the supplied page.
  """

  page.parse()

  env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
  env.filters['relpath'] = relpath
  template = env.get_template(config['template'])

  targs = config['template_arguments']
  targs.update(kwargs)
  complete = template.render(current=page, tree=tree, **targs)

  destination = os.path.join(config['site_dir'], page.url())
  if not os.path.exists(os.path.dirname(destination)):
    os.makedirs(os.path.dirname(destination))

  with open(destination, 'w') as fid:
    log.info('Creating {}'.format(destination))
    soup = bs4.BeautifulSoup(complete, 'html.parser')
    fid.write(soup.prettify().encode('utf-8'))


def build_pages(tree, **config):
  """
  Build all the pages in parallel.
  """
  jobs = []
  for page in flat(tree):
    p = multiprocessing.Process(target=build_page, args=(page, tree, config))
    p.start()
    jobs.append(p)

    for job in jobs:
      job.join()


def build(config_file='moosedocs.yml', **kwargs):
  """
  The main build command.
  """

  config = MooseDocs.yaml_load(config_file)
  config.update(kwargs)
  sitemap = MooseDocs.load_pages(config['pages'])


  # TODO: Update this to use list provide in configuration
  md_config = config['markdown_extensions'][-1]['MooseDocs.extensions.MooseMarkdown']

  moose = MooseDocs.extensions.MooseMarkdown(**md_config)
  parser = markdown.Markdown(extensions=[moose, 'markdown_include.include', 'admonition', 'mdx_math', 'toc', 'extra'])


  # Build the tree structure from the pages
  tree = NavigationNode(name='root')
  make_tree(sitemap, tree, parser)

  # Crete the html
  home = MoosePage(markdown='index.md', parser=parser)
  build_page(home, tree, config, home=True)
  build_pages(tree, **config)

  # Copy supporting files
  copy_files(**config)

  return config
