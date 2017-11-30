#pylint: disable=missing-docstring
####################################################################################################
#                                    DO NOT MODIFY THIS HEADER                                     #
#                   MOOSE - Multiphysics Object Oriented Simulation Environment                    #
#                                                                                                  #
#                              (c) 2010 Battelle Energy Alliance, LLC                              #
#                                       ALL RIGHTS RESERVED                                        #
#                                                                                                  #
#                            Prepared by Battelle Energy Alliance, LLC                             #
#                               Under Contract No. DE-AC07-05ID14517                               #
#                               With the U. S. Department of Energy                                #
#                                                                                                  #
#                               See COPYRIGHT for full restrictions                                #
####################################################################################################
#pylint: enable=missing-docstring
import os
import yaml

class IncludeLoader(yaml.Loader):
    """
    A custom loader that handles nested includes. The nested includes should use absolute paths
    from the origin yaml file.
    """
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        self.add_constructor('!include', IncludeLoader.include)
        super(IncludeLoader, self).__init__(stream)

    def include(self, node):
        """
        Allow for the embedding of yaml files.
        """
        filename = os.path.join(self._root, self.construct_scalar(node))
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return yaml.load(f, IncludeLoader)
        else:
            raise IOError("Unknown included file: {}".format(filename))

def yaml_load(filename):
    """
    Load a YAML file capable of including other YAML files.

    Args:
      filename[str]: The name to the file to load, relative to the git root directory

    http://stackoverflow.com/questions/528281/how-can-i-include-an-yaml-file-inside-another
    """

    # Attach the include constructor to our custom loader.

    with open(filename, 'r') as fid:
        yml = yaml.load(fid, IncludeLoader)

    return yml
