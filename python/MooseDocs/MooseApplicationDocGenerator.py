import os
import utils
from mkdocs.utils import yaml_load
import logging
log = logging.getLogger(__name__)

from MooseSubApplicationDocGenerator import MooseSubApplicationDocGenerator
class MooseApplicationDocGenerator(object):
    """
    Reads the main configuration yml file (e.g., docs/mkdocs.yml) and generates MOOSE system and object
    documentation.

    Args:
        root[str]: The root directory of your application.
        config_file[str]: The main documentation configuration for your application.
        exe[str]: The executable to utilize.

    Kwargs:
        develop[bool]: When True the __call__ method will always generate documentation regardless of
                       modified time of the executable.
    """

    def __init__(self, root, config_file, exe, **kwargs):
        self._root = root
        self._config_file = config_file
        self._exe = exe
        self._modified = None
        self._develop = kwargs.pop('develop', False)

    def __call__(self):
        """
        Operator(). Calling this function causes the documentation to generated.

        NOTE: Documentation will only generated if the executable has been modified since that last time
              the function has been called, unless the develop flag was set to True upon construction
              of this object.
        """
        if self._develop:
            self._generate()
            self._modified = modified

        else:
            modified = os.path.getmtime(self._exe)
            if self._modified != os.path.getmtime(self._exe):
                self._generate()
                self._modified = modified

    def _configure(self):
        """
        Build the configuration options for included sub-directories.
        """
        # Read the general yml file (e.g. mkdocs.yml)
        with open(self._config_file, 'r') as fid:
            yml = yaml_load(fid.read())

        # Global Config settings (and defaults)
        global_config = yml['extra'].get('global_config', dict())
        global_config.setdefault('build', os.path.join(self._root, 'docs', 'documentation'))
        global_config.setdefault('details', os.path.join(self._root, 'docs', 'details'))
        global_config.setdefault('docs', os.path.join(self._root, 'docs'))
        global_config.setdefault('repo', None)
        global_config.setdefault('doxygen', None)
        global_config.setdefault('hide', list())
        global_config.setdefault('links', dict())

        def update_config(dirname, cname):
            """
            Helper for updating/creating local configuration dict.
            """

            # Open the local config file
            with open(cname) as fid:
                config = yaml_load(fid.read())

            # Define abspath's for all directories supplied
            keys = ['build', 'details', 'docs']
            for key in keys:
                if key in config:
                    config[key] = os.path.abspath(os.path.join(dirname, config[key]))

            # Set the default source directory and sub-folder
            config['source'] = dirname
            config['folder'] = os.path.relpath(config['source'], os.getcwd())

            # Set the defaults
            for key, value in global_config.iteritems():
                config.setdefault(key, value)

            # Append the hide/links data
            config['hide'] = set(config['hide'] + global_config['hide'])
            config['links'].update(global_config['links'])


            # Re-define the links path relative to working directory
            for key, value in config['links'].iteritems():
                out = []
                for path in value:
                    out.append(os.path.abspath(os.path.join(dirname, path)))
                config['links'][key] = out

            return config

        #TODO: Error check for 'extra' and 'include'

        configs = []
        for include in yml['extra']['include']:
            path = os.path.join(self._root, include, 'config.yml')
            configs.append(update_config(include, path))
        return configs


    def _generate(self):
        """
        Generate the documentation.
        """

        # Some arguments to be passed in
        dirname = os.path.join(self._root)

        # Setup the location
        log.info('Generating Documentation: {}'.format(self._config_file))

        # Parse the configuration file for the desired paths
        os.chdir(dirname)
        configs = self._configure()

        # Locate and run the MOOSE executable
        print 'EXE:', self._exe
        raw = utils.runExe(self._exe, '--yaml')
        ydata = utils.MooseYaml(raw)

        for config in configs:
            generator = MooseSubApplicationDocGenerator(ydata, config)
            generator.write()
