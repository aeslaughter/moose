import re
from markdown.preprocessors import Preprocessor

class MooseMarkdownLinkPreprocessor(Preprocessor):
    """

    """

    def __init__(self, md, database, *args, **kwargs):
        super(MooseMarkdownLinkPreprocessor, self).__init__(md, *args, **kwargs)

        self._database = database

    def run(self, lines):

        print lines

        """
        for line in lines:
            match = re.search(r'\[.*?\]\((\w+\.md)\)', line)
            if match:
                name = match.group(1)
                print name
                if name in self._database:
                    print self._database[name][0].filename()
                print line
        """

        return lines
