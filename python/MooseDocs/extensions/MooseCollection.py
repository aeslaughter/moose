import re
import os

from markdown.blockprocessors import UListProcessor
from markdown.util import etree

import MooseDocs
from MooseCommonExtension import MooseCommonExtension

class MooseCollection(UListProcessor, MooseCommonExtension):
  """
  Markdown syntax for creating "collections": http://materializecss.com/collections.html
  """

  def __init__(self, parser, **kwargs):
    MooseCommonExtension.__init__(self, **kwargs)
    UListProcessor.__init__(self, parser)

    self.RE = re.compile(r'^\s{0,%d}\*-\s+(.*)' % (self.tab_length - 1))
    self.CHILD_RE = re.compile(r'^[ ]{0,%d}((\d+\.)|\*-)[ ]+(.*)' %
                               (self.tab_length - 1))

    self._settings = {'header': False}


  def run(self, parent, block):
    super(MooseCollection, self).run(parent, block)


 # def get_items(self, *args, **kwargs):
 #     items = super(MooseCollection, self).get_items(*args, **kwargs)

 #     print items
      #import sys; sys.exit()

 #     return items

  # def run(self, parent, blocks):
  #   """
  #   Convert the markdown to html for colllection list.
  #   """

  #   block = blocks.pop(0)
  #   match = self.RE.search(block)
  #   options = match.group(1)
  #   settings, styles = self.getSettings(options)

  #   ul = etree.SubElement(parent, 'ul')
  #   if settings['header']:
  #     ul.set('class', 'collection with-header')
  #   else:
  #     ul.set('class', 'collection')


  #   for item in self.items(block, header)
  #   print block
  #   print block.splitlines()
  #   sys.exit()
  #   return ul

#  def items(self, block, header=False):
