import os
import re
import logging

extensions = ('md', 'css', 'js', 'png', 'svg', 'jpg')
root = '/Users/slauae/projects/moose/framework/doc/content'
content = ['**']

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

def doc_import(root_dir, content=None, extensions=None):
    """
    Cretes a list of files to "include" from patterns.

    Args:
        root_dir[str]: The directory which all other paths should be relative to.
        content[list]: List of file/path globs to include, relative to the 'base' directory, paths
                       beginning with '!' are excluded.
        extensions[str]: Limit the search to an extension (e.g., '.md')
    """

    # Define the include/exclude/extensions lists
    if content is None:
        content = []

    # Check types
    if not isinstance(content, list) or any(not isinstance(x, str) for x in content):
        LOG.error('The "content" must be a list of str items.')
        return None

    # Loop through the base directory and create a set of matching filenames
    filenames = set()
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith(extensions) and not fname.startswith('.'):
                full_name = os.path.join(root, fname)
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
