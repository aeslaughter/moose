import os
import jinja2
import markdown
import MooseDocs
from MooseDocsMarkdownNodeBase import MooseDocsMarkdownNodeBase

def presentation_options(parser):
    """
    Command line options for the presentation generator.
    """
    reveal_default = os.path.join(os.getenv('HOME'), 'projects', 'reveal.js')

    parser.add_argument('md_file', type=str, help="The markdown file to convert to slides.")
    parser.add_argument('--output', '-o', default=None, type=str, help="The default html file to create, defaults to input filename with html extension.")
    parser.add_argument('--template', type=str, default='presentation.html', help="The template html file to utilize (default: %(default)s).")
    parser.add_argument('--title', type=str, default="MOOSE Presentation", help="The title of the document.")
    parser.add_argument('--css', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css', 'moose.css')], help="A list of additional css files to inject into the presentation html file (%(default)s).")
    parser.add_argument('--scripts', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js', 'init.js')], help="A list of additional js files to inject into the presentation html file (%(default)s).")
    return presentation

class PresentationBuilder(MooseDocsMarkdownNodeBase):

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

def presentation(config_file='moosedocs.yml', md_file=None, output=None, template=None, **template_args):
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
