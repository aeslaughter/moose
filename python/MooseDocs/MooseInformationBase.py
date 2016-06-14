import os

class MooseInformationBase(object):
    def __init__(self, node):
        self._yaml = node

    def __str__(self):
        return self.markdown()

    def markdown(self):
        pass

    def write(self, **kwargs):
        """

        """
        name = '{}.md'.format(self._yaml['name'].split('/')[-1])

        prefix = kwargs.pop('prefix', None)
        if prefix:
            if not os.path.exists(prefix):
                os.mkdir(prefix)
            name = os.path.join(prefix, name)

        name = os.path.abspath(name)
        print 'Writing:', name
        fid = open(name, 'w')
        fid.write(self.markdown())
        fid.close()
