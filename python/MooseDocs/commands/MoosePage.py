import os
import copy
import bs4
import jinja2
import logging
log = logging.getLogger(__name__)

from NavigationNode import NavigationNode


def relpath(input):
  """
  A utility function for Jinja2 template event filter.

  Args:
    input[tuple]: The os.path.relpath arguments.
  """
  if input[0].startswith('http'):
    return input[0]
  return os.path.relpath(*input)


class MoosePage(NavigationNode):
  """
  Navigation item for markdown page.

  Args:
    filename[str]: The complete markdown filename to be converted.
    parser[markdown.Markdown(): Python Markdown object instance.
    root[str]: The root directory.
  """

  def __init__(self, filename=None, parser=None, **kwargs):
    super(MoosePage, self).__init__(**kwargs)

    # Store the supplied arguments
    self._filename = filename
    self._parser = parser

    # Storage for the the html that will be generated
    self._html = None

    # Populate the list of parent nodes (i.e., "breadcrumbs")
    self._breadcrumbs = []
    def helper(node):
        if node.parent:
            self._breadcrumbs.insert(0, node)
            helper(node.parent)
    helper(self)

    # Set the URL for the page
    local = [node.name for node in self._breadcrumbs] + ['index.html']
    self._url = os.path.join(*local).lower().replace(' ', '_')

  def _string(self, level):
    """
    Overrides default to include the markdown file name in the tree dump.
    """
    return "{}{}: {}\n".format(' '*2*level, self.name, self._filename)

  def build(self, **kwargs):

    # Create a local configuration
    config = copy.copy(self.config)
    config.update(kwargs)

    # Parse the HTML
    with open(self._filename, 'r') as fid:
      md = fid.read()
    self._html = self._parser.convert(md.decode('utf-8'))

    # Create the template object
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    env.filters['relpath'] = relpath
    template = env.get_template(config['template'])

    # Render the html via template
    targs = config['template_arguments']
    targs.update(kwargs)
    complete = template.render(current=self, tree=self.root(), **targs)

    # Make sure the destination directory exists
    destination = os.path.join(self.site_dir, self.url())
    if not os.path.exists(os.path.dirname(destination)):
      os.makedirs(os.path.dirname(destination))

    # Write the file
    with open(destination, 'w') as fid:
      log.info('Creating {}'.format(destination))
      soup = bs4.BeautifulSoup(complete, 'html.parser')
      fid.write(soup.prettify().encode('utf-8'))

  def edit(self, repo_url):
    """
    Return the GitHub address for editing the markdown file.

    Args:
      repo_url[str]: Web address to use as the base for creating the edit link
    """
    return os.path.join(repo_url, 'edit', 'devel', self._filename)

  def contents(self, level='h2'):
    """
    Return the table of contents.
    """
    soup = bs4.BeautifulSoup(self._html, 'html.parser')
    for tag in soup.find_all(level):
      yield (tag.contents[0], tag.attrs['id'])


  def breadcrumbs(self):
    """
    Return the parent nodes (i.e., "breadcrumbs")
    """
    return self._breadcrumbs

  def url(self, rel=None):
    """
    Return the url to the generated page.
    """
    if rel:
      return os.path.relpath(rel.url(), self._url)
    else:
      return self._url

  def html(self):
    """
    Return the generated html from markdown.
    """
    return self._html
