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
import fnmatch
import logging

LOG = logging.getLogger(__name__)

def moose_docs_import(filename=None, include=None, exclude=None, extension='', root=os.getcwd()):
    """
    Cretes a list of files to "include" from files, include, and/or exclude lists.

    Args:
        filename[str]: File containing include/exclude glob patterns, one per line. The filename
                       should be defined relative to the root directory (see 'root').
                           docs/content/**/*.md
                           !docs/content/documentation/*
        include[list]: List of file/path globs to include, relative to the 'root' directory.
        exclude[list]: List of file/path glob patterns to exclude (do not include !), relative
                       to the 'root' directory.
        extension[str]: Limit the search to an extension (e.g., '.md')
        root[str]: The absolute path to the root directory, all include/exclude paths should be
                   defined relative to this directory. This is also the directory that is walked
                   to search for files that exists.
    """

    # Define the include/exclude lists
    if include is None:
        include = []
    if exclude is None:
        exclude = []

    # Check types
    if not isinstance(exclude, list) or any(not isinstance(x, str) for x in exclude):
        LOG.error('The "exclude" must be a list of str items.')
        return None
    if not isinstance(include, list) or any(not isinstance(x, str) for x in include):
        LOG.error('The "include" must be a list of str items.')
        return None

    # Append exclude/include lists from a file
    if filename is not None:
        filename = os.path.join(root, filename)
        if not os.path.exists(filename):
            LOG.error('The file {} does not exists.'.format(filename))
            return None
        with open(filename, 'r') as fid:
            lines = fid.readlines()

        for pattern in lines:
            if pattern.startswith('!'):
                exclude.append(pattern[1:].strip('\n'))
            else:
                include.append(pattern.strip('\n'))

    # Loop through the root directory and create a set of matching filenames
    matches = set()
    for base, _, files in os.walk(os.path.abspath(root)):
        filenames = [os.path.join(base, fname) for fname in files if fname.endswith(extension)]
        for pattern in include:
            for filename in fnmatch.filter(filenames, os.path.join(root, pattern)):
                matches.add(filename)

    # Create a remove list
    remove = set()
    for pattern in exclude:
        for filename in fnmatch.filter(matches, os.path.join(root, pattern)):
            remove.add(filename)

    # Return a sorted lists of matches
    matches -= remove
    return sorted(matches)
