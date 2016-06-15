import os

class MooseInformationBase(object):
    def __init__(self, node, **kwargs):
        self._yaml = node

        self._root = kwargs.get('root', 'docs/documentation')

        self._repo = kwargs.get('repo', None)
        self._doxygen = kwargs.get('doxygen', None)
        self._path = kwargs.get('path', '.')

        print kwargs.get('details', '.'), self.filename(node['name'])
        self._details = os.path.join(kwargs.get('details', '.'), self.filename(node['name']))


    def __str__(self):
        return self.markdown()

    def markdown(self):
        pass

    @staticmethod
    def filename(name):
        return None

    def write(self):
        """

        """

        filename = os.path.abspath(os.path.join(self._root, self._path, self.filename(self._yaml['name'])))

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        print 'Writing:', filename
        fid = open(filename, 'w')
        fid.write(self.markdown())
        fid.close()
