import os
import sys
import copy
import multiprocessing
import itertools
import markdown
import markdown_include
import bs4
import shutil
#import jinja2
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


def make_tree(pages, node, parser, site_dir, config):
  """
  Create the tree structure of NavigationNode/MoosePage objects
  """
  for p in pages:
    for k, v in p.iteritems():
      if isinstance(v, list):
        child = NavigationNode(name=k, parent=node, site_dir=site_dir, **config)
        node.children.append(child)
        make_tree(v, child, parser, site_dir, config)
      else:
        page = MoosePage(name=k, parent=node, filename=v, parser=parser, site_dir=site_dir, **config)
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
      dst_dir = os.path.dirname(dst)
      if not os.path.exists(dst_dir):
        log.debug('Creating {} directory.'.format(destination))
        os.makedirs(dst_dir)

      log.debug('Copying file {} --> {}'.format(src, dst))
      shutil.copy(src, dst)





class Builder(object):

  def __init__(self, sitemap, parser, site_dir, **config):

    self._sitemap = sitemap
    self._parser = parser
    self._site_dir = site_dir

    self._root = NavigationNode(name='root')
    make_tree(self._sitemap, self._root, self._parser, self._site_dir, config)

    self._pages = dict()
    for page in flat(self._root):
      self._pages[page.name] = page


  def add(self, filename, name='', **config):

    page = MoosePage(name=name, filename=filename, parser=self._parser, site_dir=self._site_dir, **config)
    self._pages[page.name] = page

  def build(self, name=None, **kwargs):
    """
    Build all the pages in parallel.
    """

    if name:
      if name in self._pages:
        self._pages[name].build()
      else:
        log.error("Unknown markdown page: {}".format(name))

    else:
      jobs = []
      for page in self._pages.itervalues():
        p = multiprocessing.Process(target=page.build)
        p.start()
        jobs.append(p)

      for job in jobs:
        job.join()

    self._copy_files()


  def _copy_files(self):

    copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js'),
               os.path.join(self._site_dir, 'js'), extensions=['.js'])

    copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css'),
               os.path.join(self._site_dir, 'css'), extensions=['.css'])
#  copy_files(os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'fonts'), os.path.join(config['site_dir'], 'fonts'), extensions=['.css'])

    copy_files(os.path.join(os.getcwd(), 'js'),
               os.path.join(self._site_dir, 'js'), extensions=['.js'])

    copy_files(os.path.join(os.getcwd(), 'css'),
         os.path.join(self._site_dir, 'css'), extensions=['.css'])

    copy_files(os.path.join(os.getcwd(), 'media'),
           os.path.join(self._site_dir, 'media'), extensions=['.png', '.svg'])




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

  builder = Builder(sitemap, parser, config.pop('site_dir'), **config)
  builder.add('index.md', **config)
  builder.build()

  return config
