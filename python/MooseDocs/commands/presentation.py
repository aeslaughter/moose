import os
import jinja2
import markdown
import MooseDocs
from MooseDocsMarkdownNode import MooseDocsMarkdownNode

def presentation_options(parser):
    """
    Command line options for the presentation generator.
    """
    reveal_default = os.path.join(os.getenv('HOME'), 'projects', 'reveal.js')

    parser.add_argument('input', type=str, help="The markdown file to convert to slides.")
    parser.add_argument('--output', '-o', default=None, type=str, help="The default html file to create, defaults to input filename with html extension.")
    parser.add_argument('--template', type=str, default='presentation.html', help="The template html file to utilize (default: %(default)s).")
    parser.add_argument('--title', type=str, default="MOOSE Presentation", help="The title of the document.")
    parser.add_argument('--css', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'css', 'moose.css')], help="A list of additional css files to inject into the presentation html file (%(default)s).")
    parser.add_argument('--scripts', type=str, nargs='+', default=[os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'js', 'init.js')], help="A list of additional js files to inject into the presentation html file (%(default)s).")
    return presentation

def insert_file(filename):
    """
    Helper function for jinja2 to read css file and return as string.
    """
    with open(filename, 'r') as fid:
        return fid.read().strip('\n')
    return ''

def presentation(config_file='moosedocs.yml', input=None, output=None, template=None, **template_args):
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

    # Create the jinja2 template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([os.path.join(MooseDocs.MOOSE_DIR, 'docs', 'templates'),
                                                             os.path.join(os.getcwd(), 'templates')]))
    env.globals['insert_file'] = insert_file
    template = env.get_template(template)

    # Read the markdown and convert to html
    with open(input, 'r') as fid:
        md = fid.read()
    html = parser.convert(md)

    # Inject slides into presentation template
    complete = template.render(content=html, **config['template_arguments'])

    # Write the output file
    if not output:
        name, _ = os.path.splitext(input)
        output = name + '.html'
    with open(output, 'w') as fid:
        fid.write(complete)
