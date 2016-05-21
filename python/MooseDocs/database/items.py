"""
The following objects are designed to work with the Database class,
see Database.py for usage.
"""
import os
import re
import MooseDocs

class DatabaseItem(object):
    """
    Base class for database items.

    Args:
        filename[str]: The complete filename (supplied by Database object).
    """
    def __init__(self, filename):
        self._filename = filename

    def keys(self):
        pass

    def markdown(self):
        pass

    def content(self):
        fid = open(self._filename, 'r')
        content = fid.read()
        fid.close()
        return content


class MarkdownIncludeItem(DatabaseItem):

    def keys(self):
        yield os.path.basename(self._filename)[0:-3]

    def markdown(self):
        return '{{!{}!}}'.format(self._filename)

class RegexItem(DatabaseItem):

    def __init__(self, filename, regex):
        DatabaseItem.__init__(self, filename)
        self._regex = re.compile(regex)

    def keys(self):

        for match in re.finditer(self._regex, self.content()):
            grp1 = match.group(1)
            self._rel_path = self._filename.split('/moose/')[-1]
            self._repo = MooseDocs.MOOSE_REPOSITORY + self._rel_path
            yield grp1


#            self._database[grp1].append( (rel, repo, filename) )


class InputFileItem(RegexItem):
    def __init__(self, filename):
        RegexItem.__init__(self, filename, r'type\s*=\s*(\w+)\b')

    def markdown(self):
        return '* [{}]({})'.format(self._rel_path, self._repo)

class ChildClassItem(RegexItem):
    def __init__(self, filename):
        RegexItem.__init__(self, filename, r'public\s*(\w+)\b')

    def markdown(self):
        # Check for C file
        c_rel_path = self._rel_path.replace('/include/', '/src/').replace('.h', '.C')
        c_repo = self._repo.replace('/include/', '/src/').replace('.h', '.C')
        c_filename = self._filename.replace('/include/', '/src/').replace('.h', '.C')

        if os.path.exists(c_filename):
            md = '* [{}]({})\n[{}]({})'.format(self._rel_path, self._repo, c_rel_path, c_repo)
        else:
            md = '* [{}]({})'.format(self._rel_path, self._repo)

        return md
