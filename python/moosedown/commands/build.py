"""
Defines the MooseDocs build command.
"""
import os
import copy
import logging
import importlib
import collections

import anytree
import livereload

import mooseutils

import moosedown

logging.basicConfig(level=logging.DEBUG) #TODO: need to get this into config
LOG = logging.getLogger(__name__)

# Set of extenions to load by default
DEFAULT_EXTENSIONS = ['moosedown.extensions.core',
                      'moosedown.extensions.config',
                      'moosedown.extensions.command',
                      'moosedown.extensions.include',
                      'moosedown.extensions.floats',
                      'moosedown.extensions.table',
                      'moosedown.extensions.autolink',
                      'moosedown.extensions.devel',
                      'moosedown.extensions.alert']

def command_line_options(subparser):
    """
    Define the command line options for the build command.
    """
    build_parser = subparser.add_parser('build', help='Convert markdown into HTML or LaTeX.')
    build_parser.add_argument('--lexer-components', action='store_true',
                              help='Show the lexer components in order.')

def load_extensions(node, filename):
    """
    Instatiates the Extension objects, with the configuration from the hit file, for passing
    into the Translator object.

    Inputs:
        node[hit.Node|None]: The [Extensions] section of the hit file.
    """

    # The key is the extension module name, value is a dict() of configuration options, which is
    # populated from the hit nodes and applied to the object via the make_extension method.
    ext_configs = collections.OrderedDict()
    if not (node and node.param('disable_defaults')):
        ext_configs = collections.OrderedDict()
        for key in DEFAULT_EXTENSIONS:
            ext_configs[key] = dict()

    # Process the [Extensions] block of the hit input, if it exists
    if node:
        for child in node:
            if 'type' not in child:
                msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter."
                LOG.error(msg, filename, child.line(), child.fullpath())
            else:
                config = copy.copy(child.parameters)
                ext_type = config.pop('type')
                ext_configs[ext_type] = {k:v.value for k, v in config.iteritems()}

    # Build the Extension objects
    extensions = []
    for name, config in ext_configs.iteritems():
        try:
            module = importlib.import_module(name)
            if not hasattr(module, 'make_extension'):
                msg = "The supplied module '%s' must have a 'make_extension' function."
                LOG.error(msg, module.__name__)
            else:
                extensions.append(module.make_extension(**config))

        except ImportError as e:
            msg = "Failed to import the '%s' module.\n%s"
            LOG.error(msg, name, e.message)

    return extensions

def load_object(node, filename, default, *args):
    """
    Helper for loading moosedown objects: Reader, Renderer, Translator
    """

    if node:
        if 'type' not in node:
            msg = "ERROR\n%s:%s\nThe section '%s' must contain a 'type' parameter, " \
                  "using the default %s."
            LOG.error(msg, filename, node.line(), node.fullpath(), type(default).__name__)
        else:
            config = copy.copy(node.parameters)
            config.pop('type')
            config = {k:v.value for k, v in config.iteritems()}
            try:
                return eval(node['type'])(*args, **config)
            except NameError:
                param = node.parameters['type']
                msg = "ERROR\n%s:%s\nThe parameter '%s' must contain a valid object name, using " \
                      "the default %s."
                LOG.error(msg, filename, param.line, param.fullpath)

    return default(*args)

def load_content(node, filename):
    """
    Load the [Content] block from the config.hit file.
    """
    if not node:
        msg = "The [Content] section is required within the configure file {}."
        raise KeyError(msg.format(filename))

    items = []
    for child in node:
        content = child['content'].split() if 'content' in child else []
        items.append(dict(root_dir=child['root_dir'], content=content))

    return moosedown.tree.build_page_tree.doc_tree(items)

def load_config(filename):
    """
    Read the config.hit file and create the Translator object.
    """
    node = mooseutils.hit_load(filename)

    extensions = load_extensions(node.find('Extensions'), filename)
    reader = load_object(node.find('Reader'), filename, moosedown.base.MarkdownReader)
    renderer = load_object(node.find('Renderer'), filename, moosedown.base.MaterializeRenderer)
    translator = load_object(node.find('Translator'), filename, moosedown.base.Translator,
                             reader, renderer, extensions)
    content = load_content(node.find('Content'), filename)

    return translator, content


def main(options):
    """
    Main function for the build command.
    """

    destination = os.path.join(os.getenv('HOME'), '.local', 'share', 'moose', 'site')
    logging.basicConfig(level=logging.DEBUG)
    config_file = 'config.hit'

    # TODO: add this to config.hit and command line
    #LOG.setLevel(logging.DEBUG)

    translator, root = load_config(config_file)

    #TODO: clean this up with better format and make it a function
    if options.lexer_components:
        for key, grammer in translator.reader.lexer.grammers().iteritems():
            print 'GRAMMER:', key
            for pattern in grammer:
                print '  ', pattern

    if False:
        from moosedown.tree import page
        filename = '/Users/slauae/projects/moosedown/docs/content/utilities/moosedown/test.md'
        node = page.MarkdownNode(source=filename)
        node.read()
        ast, html = translator.convert(node)
        print ast
        #print html

    else:
        server = livereload.Server()
        for node in anytree.PreOrderIter(root):
            node.base = destination
            node.init(translator)# = translator

            if node.source and os.path.isfile(node.source):
                server.watch(node.source, node.build)

            # Everything needs translator before it can build
            node.build()

        server.serve(root=destination, port=8000)
