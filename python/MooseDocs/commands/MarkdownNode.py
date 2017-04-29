import os
import logging
log = logging.getLogger(__name__)

import MooseDocs
from MooseDocsNode import MooseDocsNode

class MarkdownNode(MooseDocsNode):
    """
    Node for converting markdown to html.
    """
    def __init__(self, markdown=None, parser=None, **kwargs):
        super(MarkdownNode, self).__init__(**kwargs)

        if markdown is None:
            raise Exception('A markdown file or content must be supplied.')

        self.__parser = parser
        self.__content = None
        self.__md_file = None

        if os.path.isfile(markdown):
            self.__md_file = markdown
        else:
            self.__content = markdown

    def source(self):
        """
        Return the source markdown file.
        """
        return self.__md_file

    @property
    def content(self):
        if self.__md_file:
            with open(self.__md_file, 'r') as fid:
                self.__content = fid.read().decode('utf-8')
        return self.__content

    def convert(self):
        """
        Converts the markdown to html.
        """
        return self.__parser.convert(self)

    def build(self, lock=None):
        """
        Converts the markdown to html and writes result html to file.
        """
        self.write(self.convert(), lock)

    def write(self, content, lock=None):
        """
        Write the supplied content to the html file.
        """
        # Make sure the destination directory exists, if it already does do nothing. If it does not exist try to create
        # it, but include a try statement because it might get created by another process.
        destination = self.path()
        if lock: # Lock is not supplied or needed with build function is called from the liveserver
            with lock:
                if not os.path.exists(destination):
                    os.makedirs(destination)
        else:
            if not os.path.exists(destination):
                os.makedirs(destination)

        # Write the file
        with open(self.url(), 'w') as fid:
            log.debug('Creating {}'.format(self.url()))
            fid.write(content.encode('utf-8'))

    def url(self, parent=None):
        """
        Return the url to the page to be created.
        """
        path = self.path()
        if parent:
            path = os.path.relpath(parent.path(), path)
        return os.path.join(path, 'index.html')
