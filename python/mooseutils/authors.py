# Use python 3 non-truncating division
from __future__ import division
import os
import sys
import re
import copy
import subprocess
import collections
import argparse


Language = collections.namedtuple('Language', 'extension name comment block_comment_open block_comment_close')

languages = dict()
languages['.py'] = Language(extension='.py', name='Python', comment=['#'],
                            block_comment_open=["'''", '"""'], block_comment_close=["'''", '"""'])



def write_table(counts):


    output = ''
    for group in Authors.GROUPS:

        total = sum([c for c in counts[group].itervalues()])
        if total:
            output += group.upper() + ':\n'
            output += '-'*72 + '\n'
            output += '{:4}{:50}{:>10}{:>8}\n'.format('', 'Author', 'Count', '%')
            output += '-'*72 + '\n'
            for author, cnt in counts[group].iteritems():
                output +=  '{:4}{:50}{:10}{:8.1%}\n'.format('', author, cnt, cnt/total)

    return output




class Authors(object):

    AUTHOR_RE = re.compile('\(([\w\s\.]+)\s[0-9]{4}-')

    GROUPS = ['total', 'code', 'comments', 'blank']


    def __init__(self, filename):
        self.__filename = filename

        _, ext = os.path.splitext(self.__filename)
#        if ext not in languages:
#            raise NotImplementedError("")
        self.__language = languages[ext]

        self.__counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def filename(self):
        return self.__filename

    def counts(self):
        return self.__counts

    def increment(self, group, author):
        if group not in self.GROUPS:
            raise KeyError('Invalid group name: {}'.format(group))
        self.__counts[group][author] += 1

    def execute(self):

        try:
            output = subprocess.check_output(['git', 'blame', self.__filename]).split('\n')
        except:
            return

        in_block_comment = False

        for line in output:
            local = line.strip()
            match = self.AUTHOR_RE.search(line)
            if match:
                author = match.group(1)
            else:
                continue

            if (not in_block_comment) and any([local.startswith(x) for x in self.__language.block_comment_open]):
                in_block_comment = True
            self.increment('total', author)

            if local == '':
                self.increment('blank', author)
            elif in_block_comment or any([local.startswith(x) for x in self.__language.comment]):
                self.increment('comments', author)
            else:
                self.increment('code', author)

            if (in_block_comment) and any([local.startswith(x) for x in self.__language.block_comment_close]):
                in_block_comment = False











if __name__ == '__main__':

    exclude = [os.path.join(os.path.dirname(__file__), '..', '..', 'framework', 'contrib')]

    parser = argparse.ArgumentParser(description='Determine the authors')
    parser.add_argument('locations', type=str, nargs='+', default=os.getcwd(),
                        help='A list of working directories to inspect (Default: %(default)).')
    parser.add_argument('--exclude', type=str, nargs='+', default=exclude)
    args = parser.parse_args()

    objects = []
    for location in args.locations:
        for root, dirs, filenames in os.walk(location):
            dirs[:] = [d for d in dirs if d not in args.exclude]
            for filename in filenames:
                full_file = os.path.abspath(os.path.join(root, filename))
                objects.append(Authors(full_file))


    for obj in objects:
        obj.execute()

    counts = collections.defaultdict(lambda: collections.defaultdict(int))
    for obj in objects:
        #print obj.filename()
        for name, value in obj.counts().iteritems():
            for author, count in value.iteritems():
                #print ' '*4, name, author, count
                counts[name][author] += count

    print write_table(counts)
