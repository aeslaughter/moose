import os
import logging

class MooseInformationBase(object):

    log = logging.getLogger('MkMooseDocs.MooseInformationBase')

    def __init__(self, node, **kwargs):
        self._yaml = node
        self._config = kwargs

        print self._config['details'], self.filename(node['name'])
        import sys; sys.exit()
        #self._details_abspath = os.path.abspath(os.path.join(self._config['details'], self.filename(node['name'])))
        #self._details = os.path.relpath(self._details_abspath, os.path.abspath(self._config['docs']))


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
        filename = os.path.abspath(os.path.join(self._config['build'], self._config['source'], self.filename(self._yaml['name'])))

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        md = self.markdown()

        # Do not re-write file if it exists (saves mkdocs from re-loading the world)
        if os.path.exists(filename):
            with open(filename, 'r') as fid:
                content = fid.read()

            if content == md:
                return

        self.log.info('Writing: {}'.format(filename))
        fid = open(filename, 'w')
        fid.write(md)
        fid.close()
