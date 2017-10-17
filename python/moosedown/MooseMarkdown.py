import base
import common
import importlib

class MooseMarkdown(base.Translator):

    @staticmethod
    def getConfig():
        config = base.Translator.getConfig()
        config['materialize'] = (False, 'Enable the use of the Materialize framework for HTML output.')
        return config

    def __init__(self, ext=None):

        extensions = ['extensions.core', 'extensions.devel']
        if ext is not None:
            extensions += ext

        config = self.getConfig()
        reader_extensions = []
        render_extensions = []
        for ext in extensions:
            if isinstance(ext, str):
                module = importlib.import_module(ext)
            else:
                module = ext

            #TODO: test for 'make_extension'
            reader_ext, render_ext = module.make_extension()
            #TODO: check return types

            config.update(reader_ext.getConfig())
            config.update(render_ext.getConfig())

            reader_extensions.append(reader_ext)
            render_extensions.append(render_ext)

        #local = dict(commands=['extensions.command.CodeCompare'])
        #for key, value
        for reader_ext, render_ext in zip(reader_extensions, render_extensions):
            reader_ext.update(config)
            render_ext.update(config)

        reader = base.MarkdownReader(reader_extensions)

        if config['materialize']:
            render = base.MaterializeRenderer(render_extensions)
        else:
            render = base.HTMLRenderer(render_extensions)

        super(MooseMarkdown, self).__init__(reader, render)
