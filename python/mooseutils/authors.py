# Use python 3 non-truncating division
from __future__ import division
import os
import sys
import re
import copy
import subprocess
import collections
import argparse
import bisect
import multiprocessing

import mooseutils

Language = collections.namedtuple('Language', 'extensions comment block_comment')

def write_table(counts):
    """
    Create table of line ownership per author.
    """

    # Define format strings
    n = len(Authors.GROUPS)
    h_fmt = '{:50}' + '{:>10}' * n + '{:>8}\n'
    d_fmt = '{:50}' + '{:10}' * n + '{:8.2%}\n'
    hline = '-' * (50 + 10*n + 8) + '\n'

    # Compute totals
    totals = collections.defaultdict(int)
    authors = []
    total = 0
    for k, v in counts.iteritems():
        authors.append((k, v['all']))
        total += v['all']
        for group, cnt in v.iteritems():
            totals[group] += cnt

    # Sort the authors by total lines
    authors = sorted(authors, key=lambda x: x[1])

    # Create the table
    output = hline
    header = ['Author'] + [x.title() for x in Authors.GROUPS] + ['%']
    output += h_fmt.format(*header)
    output += hline
    for author, _ in reversed(authors):
        out = [author]
        for group in Authors.GROUPS:
            out.append(counts[author][group])
        out.append(counts[author]['all']/total)
        output += d_fmt.format(*out)

    output += hline
    out = [''] + [totals[g] for g in Authors.GROUPS] + ['100%']
    output += h_fmt.format(*out)
    return output

class Authors(object):
    """
    Class for populating line counts by author.
    """

    AUTHOR_RE = re.compile('\(([\w\s\.]+)\s[0-9]{4}-.*?\)\s+(.*?)$')

    GROUPS = ['code', 'comment', 'blank', 'all']

    LANGUAGES = dict()
    LANGUAGES['Python'] = Language(extensions=['.py'],
                                   comment='#',
                                   block_comment=[('"""', '"""'), ("'''", "'''")])
    LANGUAGES['C++'] = Language(extensions=['.C', '.h'],
                                comment='//',
                                block_comment=[('/\*', '\*/')])
    LANGUAGES['MOOSE Input'] = Language(extensions=['.i'],
                                        comment='#',
                                        block_comment=[])

    def __init__(self, key, filename):
        self.__key = key
        self.__filename = filename
        self.__language = self.LANGUAGES[key]
        self.__counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def counts(self):
        """Return author counts."""
        return self.__counts

    def filename(self):
        """Return the full filename."""
        return self.__filename

    def key(self):
        """Return the language key"""
        return self.__key

    """
    def flags(blame):

        n = len(lines)
        flags = ['CODE']*n

        in_block = False
        for delim in language.block_comment:
            for i, line in enumerate(lines):
                local = line.strip()
                if not in_block and local.startswith(delim[0]):
                    flags[i] = 'COMMENT'
                    in_block = True
                    if local.replace(delim[0], '', 1).endswith(delim[1]):
                        in_block = False
                elif in_block and local.endswith(delim[1]):
                    flags[i] = 'COMMENT'
                    in_block = False
                elif in_block:
                    flags[i] = 'COMMENT'
                elif local == '':
                    flags[i] = 'BLANK'
                elif local.startswith(language.comment):
                    flags[i] = 'COMMENT'
        return flags
    """

    def execute(self, blame=None):
        """Compute the author line counts."""

        # Get the 'git blame' if not provided
        if not blame:
            blame = git_blame(self.__filename)

        # Loop through lines
        in_block = False
        for i, line in enumerate(blame):
            match = self.AUTHOR_RE.search(line)
            if not match:
                continue

            author = match.group(1).strip()
            local = match.group(2).strip()
            self._increment('all', author)

            for delim in self.__language.block_comment: #todo: not correct
                if not in_block and local.startswith(delim[0]):
                    self._increment('comment', author)
                    in_block = True
                    if local.replace(delim[0], '', 1).endswith(delim[1]):
                        in_block = False
                elif in_block and local.endswith(delim[1]):
                    self._increment('comment', author)
                    in_block = False
                elif in_block:
                    self._increment('comment', author)
                elif local == '':
                    self._increment('blank', author)
                elif local.startswith(self.__language.comment):
                    self._increment('comment', author)
                else:
                    self._increment('code', author)

    def _increment(self, group, author):
        """Increment the author counter for the given group."""
        if group not in self.GROUPS:
            raise KeyError('Invalid group name: {}'.format(group))
        self.__counts[author][group] += 1

def git_blame(filename):
    return subprocess.check_output(['git', 'blame', filename]).split('\n')

def merge(objects):
    counts = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    for obj in objects:
        for name, value in obj.counts().iteritems():
            for author, count in value.iteritems():
                counts[obj.key()][name][author] += count
    return counts



if __name__ == '__main__':

    exclude = ['contrib', '.libs', '.git']

    parser = argparse.ArgumentParser(description='Determine the authors')
    parser.add_argument('locations', type=str, nargs='+', default=os.getcwd(),
                        help='A list of working directories to inspect (Default: %(default)).')
    parser.add_argument('--exclude', type=str, nargs='+', default=exclude,
                        help="List of directories to exclude from analysis.")
    parser.add_argument('--num-threads', '-j', type=int, default=multiprocessing.cpu_count(),
                        help="Specify the number of threads to build pages with.")

    args = parser.parse_args()

    # Create an Authors object for each file
    objects = []
    for location in args.locations:
        for root, dirs, _ in os.walk(location, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for d in dirs:
                for filename in subprocess.check_output(['git', 'ls-files', os.path.join(root, d)]).split('\n'):
                    full_file = os.path.abspath(filename)
                    _, ext = os.path.splitext(filename)
                    for key, lang in Authors.LANGUAGES.iteritems():
                        if ext in lang.extensions:
                            objects.append(Authors(key, full_file))


    p = multiprocessing.Pool(args.num_threads)
    blames = p.map(git_blame, [obj.filename() for obj in objects])

    for obj, blame in zip(objects, blames):
        obj.execute(blame=blame)

    counts = merge(objects)


    # Write tables
    for key, value in counts.iteritems():
        print key
        print write_table(value), '\n'
