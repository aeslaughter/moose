import os

class MooseInformationBase(object):
    def __init__(self, node):
        self._yaml = node

    def __str__(self):
        return self.markdown()

    def markdown(self):
        pass

    @staticmethod
    def filename(name):
        return None

    def write(self, **kwargs):
        """

        """
        prefix = kwargs.pop('prefix', '')

        filename = os.path.abspath(os.path.join(prefix, self.filename(self._yaml['name'])))

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.mkdirs(dirname)

        print 'Writing:', filename
        fid = open(filename, 'w')
        fid.write(self.markdown())
        fid.close()
