"""Tools for building file trees for MooseDocs"""
import os
import re
import logging

import moosedown
from moosedown.tree import page

LOG = logging.getLogger(__name__)

def build_regex(pattern):
    """
    Build regex from paths with * and **.

    When defining a content file it is useful to simply use * and ** in glob like fashion for
    directory names. However, ** in glob for python 2.7 is not supported. Therefore, this function
    mimics this behavior using regexes.

    This function replaces * with a regex that will match any characters, except a slash,
    in between forward slashes or at the beginning and end of the path.

    Similarly, the ** will match any character, including a slash, in between forward slashes or
    at the beginning or end of the string.

    """
    out = pattern.replace('.', r'\.')

    # Replace ** or * that is proceeded by the beginning of the string or a forward slash and
    # that is followed by a forward or the end of the string. The replacement is a regex that will
    # mimic the glob ** and * behaviors.
    #    ** becomes (?:.*?) which matches any character
    #    * becomes (?:[^.]?) which matches any character except for the slash
    out = re.sub(r'(?!<^|/)(\*{2})(?=/|$)', r'(?:.*?)', out, flags=re.MULTILINE)
    out = re.sub(r'(?!<^|/)(\*{1})(?=/|$)', r'(?:[^/]*?)', out, flags=re.MULTILINE)

    # The overall regex for searching filenames must be limited to one line
    return r'^{}$'.format(out)

def find_files(filenames, pattern):
    """
    Locate files matching the given pattern.
    """
    out = set()
    regex = build_regex(pattern)
    for match in re.finditer(regex, '\n'.join(filenames), flags=re.MULTILINE):
        out.add(match.group(0))
    return out

def doc_import(root_dir, content=None):
    """
    Cretes a list of files to "include" from patterns.

    Args:
        root_dir[str]: The directory which all other paths should be relative to.
        content[list]: List of file/path globs to include, relative to the 'base' directory, paths
                       beginning with '!' are excluded.
    """

    # Define the include/exclude/extensions lists
    if content is None:
        content = []

    # Check types
    if not isinstance(content, list) or any(not isinstance(x, str) for x in content):
        LOG.error('The "content" must be a list of str items.')
        return None

    # Check root_dir
    root_dir = os.path.join(moosedown.ROOT_DIR, root_dir)
    if not os.path.isdir(root_dir):
        LOG.error('The "root_dir" must be a valid directory.')
        return None

    # Loop through the base directory and create a set of matching filenames
    filenames = set()
    for root, _, files in os.walk(root_dir):
        for fname in files:
            full_name = os.path.join(root, fname)
            if os.path.isfile(full_name):
                filenames.add(full_name)

    # Build include/exclude lists
    include = []
    exclude = []
    for item in content:
        if item.startswith('!'):
            exclude.append(item)
        else:
            include.append(item)

    # Create the complete set of files
    output = set()
    for pattern in include:
        output.update(find_files(filenames, os.path.join(root_dir, pattern)))

    for pattern in exclude:
        output -= find_files(output, os.path.join(root_dir, pattern))

    return sorted(output)


def create_file_node(parent, name, filename):
    """
    Create the correct node object for the given extension.
    """
    _, ext = os.path.splitext(filename)
    if ext == '.md':
        return page.MarkdownNode(parent, name=name, source=filename)
    else:
        return page.FileNode(parent, name=name, source=filename)


def doc_tree(items):
    """
    Create a tree of files for processing.

    Inputs:
        inputs: [list[dict(),...] A list of dict items, each dict entry must contain the 'root_dir'
                and 'content' fields that are passed to the doc_import function.
    """
    # Error checking
    if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
        LOG.error('The suplied items must be a list of dict items, each with a "root_dir" and '
                  '"content" entry.')
        return None


    # Define a dict for storing nodes by path
    nodes = dict()

    # Create the root node
    nodes[()] = page.DirectoryNode(source='')

    # Create the file tree
    for value in items:

        if ('root_dir' not in value) or ('content' not in value):
            LOG.error('The suplied items must be a list of dict items, each with a "root_dir" and '
                      '"content" entry.')

        root = os.path.join(moosedown.ROOT_DIR, value['root_dir'])
        files = doc_import(root, content=value['content'])

        for filename in files:
            key = tuple(filename.replace(root, '').strip('/').split('/'))

            # Create directory nodes if they don't exist
            for i in range(1, len(key)):
                dir_key = key[:i]
                if dir_key not in nodes:
                    nodes[dir_key] = page.DirectoryNode(nodes[key[:i-1]],
                                                        name=key[i-1],
                                                        source=os.path.join(root, *dir_key))

            # Create the file node
            nodes[key] = create_file_node(nodes[key[:-1]], key[-1], filename)

    return nodes[()]
