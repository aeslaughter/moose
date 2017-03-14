import os
import markdown
import collections
import cPickle as pickle
import logging
log = logging.getLogger(__name__)

from MooseObjectSyntax import MooseObjectSyntax
from MooseParameters import MooseParameters
from MooseDescription import MooseDescription
from MooseActionSyntax import MooseActionSyntax
from MooseEquationReference import MooseEquationReference
from MooseInlineProcessor import MooseInlineProcessor
from MooseSlider import MooseSlider
from MooseActionList import MooseActionList
import MooseDocs
import mooseutils

class MooseMarkdownExtension(markdown.Extension):
    """
    Extensions that comprise the MOOSE flavored markdown.
    """

    def __init__(self, **kwargs):

        # Storage for the MooseLinkDatabase object
        self.syntax = None

        # Define the configuration options
        self.config = dict()
        self.config['executable']    = ['', "The executable to utilize for generating application syntax."]
        self.config['locations']     = [dict(), "The locations to parse for syntax."]
        self.config['repo']          = ['', "The remote repository to create hyperlinks."]
        self.config['links']         = [dict(), "The set of paths for generating input file and source code links to objects."]
        self.config['install']       = ['', "The location to install system and object documentation."]

        # Construct the extension object
        super(MooseMarkdownExtension, self).__init__(**kwargs)

        # Create the absolute path to the executable
        self.setConfig('executable', MooseDocs.abspath(self.getConfig('executable')))

    def execute(self):
        """
        Execute the supplied MOOSE application and return the YAML.
        """

        cache = os.path.join(MooseDocs.TEMP_DIR, 'moosedocs.yaml')
        exe = self.getConfig('executable')

        if os.path.exists(cache) and (os.path.getmtime(cache) >= os.path.getmtime(cache)):
            with open(cache, 'r') as fid:
                log.debug('Reading MooseYaml Pickle: ' + cache)
                return mooseutils.MooseYaml(pickle.load(fid))

        elif not (exe or os.path.exists(exe)):
            log.critical('The executable does not exist: {}'.format(exe))
            raise Exception('Critical Error')

        else:
            log.debug("Executing {} to extract syntax.".format(exe))
            try:
                raw = mooseutils.runExe(exe, '--yaml')
                with open(cache, 'w') as fid:
                    log.debug('Writing MooseYaml Pickle: ' + cache)
                    pickle.dump(raw, fid)
                return mooseutils.MooseYaml(raw)
            except:
                log.critical('Failed to read YAML file, MOOSE and modules are likely not compiled correctly.')
                raise Exception('Critical Error')


    def extendMarkdown(self, md, md_globals):
        """
        Builds the extensions for MOOSE flavored markdown.
        """
        md.registerExtension(self)

        # Create a config object
        config = self.getConfigs()

        # Extract YAML
        exe_yaml = self.execute()

        # Generate YAML data from application
        # Populate the database for input file and children objects
        log.debug('Creating input file and source code use database.')
        database = MooseDocs.MooseLinkDatabase(**config)

        # Populate the syntax
        self.syntax = collections.OrderedDict()
        for item in config['locations']:
            key = item.keys()[0]
            options = item.values()[0]
            options.setdefault('group', key)
            options.setdefault('name', key.replace('_', ' ').title())
            options.setdefault('install', config['install'])
            self.syntax[key] = MooseDocs.MooseApplicationSyntax(exe_yaml, **options)

        # Replace the InlineTreeprocessor with the MooseInlineProcessor, this allows
        # for an initialize() method to be called prior to the convert for re-setting state.
        md.treeprocessors['inline'] = MooseInlineProcessor(markdown_instance=md, **config)

        # Block processors
        md.parser.blockprocessors.add('slider', MooseSlider(md.parser, **config), '_begin')

        # Inline Patterns
        params = MooseParameters(markdown_instance=md, syntax=self.syntax, **config)
        md.inlinePatterns.add('moose_parameters', params, '_begin')

        desc = MooseDescription(markdown_instance=md, syntax=self.syntax, **config)
        md.inlinePatterns.add('moose_description', desc, '_begin')

        object_markdown = MooseObjectSyntax(markdown_instance=md, syntax=self.syntax, database=database, **config)
        md.inlinePatterns.add('moose_object_syntax', object_markdown, '_begin')

        system_markdown = MooseActionSyntax(markdown_instance=md, syntax=self.syntax, **config)
        md.inlinePatterns.add('moose_system_syntax', system_markdown, '_begin')

        system_list = MooseActionList(markdown_instance=md, yaml=exe_yaml, syntax=self.syntax, **config)
        md.inlinePatterns.add('moose_system_list', system_list, '_begin')

        md.inlinePatterns.add('moose_equation_reference', MooseEquationReference(markdown_instance=md, **config), '<moose_figure_reference')


def makeExtension(*args, **kwargs):
    return MooseMarkdownExtension(*args, **kwargs)
