class NavigationNode(object):
  """
  Class for building navigation tree for website.

  Args:
    name[str]: The name of the node.
    parent[NavigationNode]: The parent node in tree.
  """
  def __init__(self, name='', parent=None):
    self.name = name
    self.parent = parent
    self.children = []

  def __eq__(self, other):
    """
    Tests if this object is equivalent to the supplied object.
    """
    return isinstance(other, self.__class__) and self.name == other.name and self.parent == other.parent and self.children == other.children

  def __str__(self):
    """
    Allows 'print' to dump the complete tree structure.
    """
    return self._string()

  def url(self, **kwargs):
    """
    Return the url() for the node.
    """
    for child in self.children:
      if child.name == 'Overview':
        return child.url()
    return None

  def _string(self, level=0):
    """
    Helper function for dumping the tree.
    """
    output = "{}{}\n".format(' '*2*level, self.name)
    for child in self.children:
      output += child._string(level=level+1)
    return output
