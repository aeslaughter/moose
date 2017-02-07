# Use python 3 non-truncating division
from __future__ import division
import os
import sys
import re
import copy
import subprocess
import collections
import argparse


Language = collections.namedtuple('Language', 'extensions comment block_comment_open block_comment_close')




def write_table(counts):

    n = len(Authors.GROUPS)
    h_fmt = '{:50}' + '{:>10}{:>8}' * n + '\n'
    d_fmt = '{:50}' + '{:10}{:8.1%}' * n + '\n'

    h1 = '{:50}' + '{:>18}' * n + '\n'
    hline = '-' * (50 + 18*n) + '\n'

    output = ''

    totals = collections.defaultdict(int)
    authors = []
    total = 0
    for k, v in counts.iteritems():
        authors.append((k, v['all']))
        for group, cnt in v.iteritems():
            total += cnt
            totals[group] += cnt

    authors = sorted(authors, key=lambda x: x[1])


    output += hline
    output += h1.format('', *[x.upper() for x in Authors.GROUPS])
    output += h_fmt.format('Author', *['Count', '%']*n)
    output += hline
    for author, _ in reversed(authors):
        out = [author]
        for group in Authors.GROUPS:
            cnt = counts[author][group]
            out += [cnt, cnt/total]
        output += d_fmt.format(*out)

    output += hline
    output += h1.format('', *[totals[g] for g in Authors.GROUPS])
    return output




class Authors(object):

    AUTHOR_RE = re.compile('\(([\w\s\.]+)\s[0-9]{4}-.*?\)\s+(.*?)$')

    GROUPS = ['all', 'code', 'comments', 'blank']

    LANGUAGES = dict()
    LANGUAGES['Python'] = Language(extensions=['.py'], comment=['#'],
                                   block_comment_open=["'''", '"""'], block_comment_close=["'''", '"""'])
    LANGUAGES['C++'] = Language(extensions=['.C', '.h'], comment=['//'],
                                block_comment_open=['/*'],
                                block_comment_close=['*/'])

    def __init__(self, lang, filename):
        self.__name = lang
        self.__filename = filename
        self.__language = self.LANGUAGES[lang]

        self.__counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def filename(self):
        return self.__filename

    def counts(self):
        return self.__counts

    def language(self):
        return self.__name

    def increment(self, group, author):
        if group not in self.GROUPS:
            raise KeyError('Invalid group name: {}'.format(group))
        self.__counts[author][group] += 1

    def execute(self):

        try:
            output = subprocess.check_output(['git', 'blame', self.__filename]).split('\n')
        except:
            return

        in_block_comment = False

        for line in output:
            match = self.AUTHOR_RE.search(line)
            if match:
                author = match.group(1).strip()
                local = match.group(2).strip()
            else:
                continue

            if (not in_block_comment) and any([local.startswith(x) for x in self.__language.block_comment_open]):
                in_block_comment = True
            self.increment('all', author)

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
        for root, _, _ in os.walk(location):
            if root not in args.exclude:
                filenames = subprocess.check_output(['git', 'ls-files', root]).split('\n')
                for filename in filenames:
                    full_file = os.path.abspath(filename)
                    _, ext = os.path.splitext(filename)
                    for key, lang in Authors.LANGUAGES.iteritems():
                        if ext in lang.extensions:
                            objects.append(Authors(key, full_file))


    for obj in objects:
        obj.execute()

    counts = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    for obj in objects:
        for name, value in obj.counts().iteritems():
            for author, count in value.iteritems():
                counts[obj.language()][name][author] += count

    for key, value in counts.iteritems():
        print key
        print write_table(value)
        print '\n\n'
