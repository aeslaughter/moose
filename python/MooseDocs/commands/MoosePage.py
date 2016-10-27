import os
import bs4

from NavigationNode import NavigationNode

class MoosePage(NavigationNode):
  """
  Navigation item for markdown page.

  Args:
    markdown[str]: The complete markdown filename to be converted.
    parser[markdown.Markdown(): Python Markdown object instance.
    root[str]: The root directory.
  """

  def __init__(self, markdown=None, parser=None, **kwargs):
    super(MoosePage, self).__init__(**kwargs)

    # Store the supplied arguments
    self._markdown = markdown
    self._parser = parser

    # Storage for the theml that will be generated
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
    return "{}{}: {}\n".format(' '*2*level, self.name, self._markdown)


  def edit(self, repo_url):
    """
    Return the GitHub address for editing the markdown file.

    Args:
      repo_url[str]: Web address to use as the base for creating the edit link
    """
    return os.path.join(repo_url, 'edit', 'devel', self._markdown)

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

  def parse(self):
    """
    Convert the markdown to html.
    """
    with open(self._markdown, 'r') as fid:
      md = fid.read()
    self._html = self._parser.convert(md.decode('utf-8'))
