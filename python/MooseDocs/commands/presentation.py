import os
import shutil
import livereload
import jinja2
import markdown
import MooseDocs
from MooseDocsMarkdownNodeBase import MooseDocsMarkdownNodeBase
import logging
log = logging.getLogger(__name__)

def presentation_options(parser):
    """
    Command line options for the presentation generator.
    """
    parser.add_argument('md_file', type=str, help="The markdown file to convert to slides.")
    parser.add_argument('--serve', action='store_true', help="Serve the presentation with live reloading.")
    parser.add_argument('--host', default='127.0.0.1', type=str, help="The local host location for live web server (default: %(default)s).")
    parser.add_argument('--port', default='8000', type=str, help="The local host port for live web server (default: %(default)s).")
    parser.add_argument('--config-file', type=str, default=os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'moosedocs.yml'), help="The configuration file to use for building the documentation using MOOSE. (Default: %(default)s)")
    parser.add_argument('--output', '-o', default=None, type=str, help="The default html file to create, defaults to input filename with html extension.")
    parser.add_argument('--template', type=str, default='presentation.html', help="The template html file to utilize (default: %(default)s).")
    parser.add_argument('--title', type=str, default="MOOSE Presentation", help="The title of the document.")
    parser.add_argument('--css', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css', 'moose.css')], help="A list of additional css files to inject into the presentation html file (%(default)s).")
    parser.add_argument('--scripts', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js', 'init.js')], help="A list of additional js files to inject into the presentation html file (%(default)s).")
    return presentation

class PresentationBuilder(MooseDocsMarkdownNodeBase):
    """
    Utilize the base website node object to build presentations.
    """

    def environment(self):
        """
        Override base to add file insert filter.
        """
        env = super(PresentationBuilder, self).environment()
        env.globals['insert_file'] = self.insertFile
        return env

    @staticmethod
    def insertFile(filename):
        """
        Helper function for jinja2 to read css file and return as string.
        """
        with open(filename, 'r') as fid:
            return fid.read().strip('\n')
            return ''

    def finalize(self, soup):
        """
        Adds a copy of image files to the destination directory.
        """
        soup = super(PresentationBuilder, self).finalize(soup)
        for img in soup('img'):
            name = os.path.basename(img['src'])
            dest = os.path.join(self.path(), name)
            dirname = os.path.dirname(dest)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            log.debug('Copying images: {} to {}'.format(img['src'], dest))
            shutil.copyfile(img['src'], dest)
            img['src'] = name
        return soup


def presentation(config_file=None, md_file=None, output=None, template=None, serve=None, port=None, host=None, **template_args):
    """
    MOOSE markdown presentation blaster.
    """

    # Load the YAML configuration file
    config = MooseDocs.load_config(config_file)
    config['template_arguments'].update(template_args)

    # Create the markdown parser, being sure to enable
    extensions, extension_configs = MooseDocs.get_markdown_extensions(config)
    extensions.append('MooseDocs.extensions.MooseMarkdownPresentation')
    parser = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)

    site_dir, _ = os.path.splitext(md_file)
    root = PresentationBuilder(name='', md_file=md_file, parser=parser, template=template, template_args=template_args, site_dir=site_dir)
    root.build()

    if serve:
        server = livereload.Server()
        server.watch(md_file, root.build)
        server.serve(root=site_dir, host=host, port=port, restart_delay=0)
