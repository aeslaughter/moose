#pylint: disable=missing-docstring
#################################################################
#                   DO NOT MODIFY THIS HEADER                   #
#  MOOSE - Multiphysics Object Oriented Simulation Environment  #
#                                                               #
#            (c) 2010 Battelle Energy Alliance, LLC             #
#                      ALL RIGHTS RESERVED                      #
#                                                               #
#           Prepared by Battelle Energy Alliance, LLC           #
#             Under Contract No. DE-AC07-05ID14517              #
#              With the U. S. Department of Energy              #
#                                                               #
#              See COPYRIGHT for full restrictions              #
#################################################################
import markdown
from markdown.preprocessors import Preprocessor

from MooseCommonExtension import MooseCommonExtension

class GlobalExtension(markdown.Extension):
    """
    Extension for adding global markdown style link ids.
    """

    def __init__(self, **kwargs):
        self.config = dict()
        self.config['globals'] = ['', "List of global markdown links (e.g., [foo]: bar)."]
        super(GlobalExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        """
        Adds Bibtex support for MOOSE flavored markdown.
        """
        md.registerExtension(self)
        config = self.getConfigs()
        md.preprocessors.add('moose_globals',
                             GlobalPreprocessor(markdown_instance=md, **config), '_begin')

def makeExtension(*args, **kwargs): #pylint: disable=invalid-name
    return GlobalExtension(*args, **kwargs)

class GlobalPreprocessor(MooseCommonExtension, Preprocessor):
    """
    Appends global links to markdown content
    """
    @staticmethod
    def defaultSettings():
        return dict() # this extension doesn't have settings

    def __init__(self, markdown_instance=None, **kwargs):
        MooseCommonExtension.__init__(self, **kwargs)
        Preprocessor.__init__(self, markdown_instance)
        self._globals = kwargs.pop('globals', dict())

    def run(self, lines):
        """
        Append globals
        """
        return lines + ['[{}]: {}'.format(key, value) for key, value in self._globals.iteritems()]
