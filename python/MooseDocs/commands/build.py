import os
import sys
import copy
import multiprocessing
import itertools
import markdown
import markdown_include
import bs4
import shutil
from distutils.dir_util import copy_tree
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


def make_tree(pages, node, parser, site_dir, template, config):
  """
  Create the tree structure of NavigationNode/MoosePage objects
  """
  for p in pages:
    for k, v in p.iteritems():
      if isinstance(v, list):
        child = NavigationNode(name=k, parent=node, site_dir=site_dir, template=template, **config)
        node.children.append(child)
        make_tree(v, child, parser, site_dir, template, config)
      else:
        page = MoosePage(name=k, parent=node, filename=v, parser=parser, site_dir=site_dir, template=template, **config)
        node.children.append(page)


def flat(node):
  """
  Create a flat list of pages for parsing and generation.

  Args:
    node[NavigationNode]: The root node to flatten from
  """
  for child in node.children:
    if isinstance(child, MoosePage):
      yield child
    for c in flat(child):
      yield c


def get_markdown_extensions(config):
  """
  Extract the markdown extensions and associated configurations from the yaml configuration.
  """
  extensions = []
  extension_configs = []
  for extension in config['markdown_extensions']:
    if isinstance(extension, dict):
      for k, v in extension.iteritems(): # there should only be one entry, but just in case
        extensions.append(k)
        extension_configs.append(v)
    else:
      extensions.append(extension)
      extension_configs.append(dict())

  return extensions, extension_configs


class Builder(object):
  """
  Object for building
  """
  def __init__(self, sitemap, parser, site_dir, template, **config):

    self._sitemap = sitemap
    self._parser = parser
    self._site_dir = site_dir
    self._template = template
    self._config = config

    self._root = NavigationNode(name='root')
    make_tree(self._sitemap, self._root, self._parser, self._site_dir, self._template, self._config)

    self._pages = dict()
    for page in flat(self._root):
      self._pages[page.name] = page

  def __iter__(self):
    """
    Allow direct iteration over pages contained in this object.
    """
    return self._pages.itervalues()


  def add(self, filename, template, name='', **kwargs):
    """
    Add additional stand-along pages.

    This is utilized to create a home page that looks different.
    """

    config = copy.copy(self._config)
    config.update(kwargs)

    page = MoosePage(name=name, filename=filename, parser=self._parser, site_dir=self._site_dir, template=template, **config)
    page.parent = self._root
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

      self.copyFiles()


  def copyFiles(self):
    """
    Copy the css/js/fonts/media files for this project.
    """

    def helper(src, dst):
      if not os.path.exists(dst):
        os.makedirs(dst)
      copy_tree(src, dst)

    # Copy js/css/fonts from MOOSE and current projects
    for from_dir in [os.path.join(MooseDocs.MOOSE_DIR, 'docs'), os.getcwd()]:
      helper(os.path.join(from_dir, 'js'), os.path.join(self._site_dir, 'js'))
      helper(os.path.join(from_dir, 'css'), os.path.join(self._site_dir, 'css'))
      helper(os.path.join(from_dir, 'fonts'), os.path.join(self._site_dir, 'fonts'))

    # Copy local medai
    helper(os.path.join(os.getcwd(), 'media'), os.path.join(self._site_dir, 'media'))


def build(config_file='moosedocs.yml', **kwargs):
  """
  The main build command.
  """

  # Load the YAML configuration file
  config = MooseDocs.yaml_load(config_file)
  config.update(kwargs)

  # Load the site map
  sitemap = MooseDocs.load_pages(config['pages'])

  # Create the markdown parser
  extensions, extension_configs = get_markdown_extensions(config)
  parser = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)

  # Create object for storing pages to be generated
  builder = Builder(sitemap, parser, config['site_dir'], config['template'], **config['template_arguments'])

  # Build "extra" pages (i.e., the home page)
  if 'extra_pages' in config:
    for extra in config['extra_pages']:
      for name, kwargs in extra.iteritems():
        kwargs.setdefault('template_arguments', dict())
        builder.add(kwargs.pop('filename'), kwargs['template'], name=name, **kwargs['template_arguments'])

  # Create the html
  builder.build()
  return config, parser, builder
