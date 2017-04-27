import os
import mooseutils
import MooseDocs

class MooseDocsNode(object):
    """
    General node for creating tree structure of documentation.

    This serves as the base class for other node objects that create content; this base node is a place holder node
    that doesn't contain any markdown content.

    The main purpose of the nodes is to accept the necessary "state" in the object construction, but the build() method
    actually performs the work. This allows the nodes to be executed by multithreading.
    """

    def __init__(self, name=None, site_dir=os.path.relpath(os.getcwd()), parent=None):

        if (name is None) or (not isinstance(name, str)):
            raise mooseutils.MooseException('The "name" string must be supplied to the MooseDocsNode object.')

        if (site_dir is None) or (not isinstance(site_dir, str)) or not os.path.isdir(site_dir):
            raise mooseutils.MooseException('The "site_dir" must be a string and a valid directory.')


        self.__name = name
        self.__site_dir = site_dir
        self.__parent = parent
        self.__children = []

        # Automatically add the child to parent
        if self.__parent:
            self.__parent.append(self)

    def __iter__(self):
        """
        Make this object iterate over the children automatically.
        """
        for child in self.__children:
            yield child

    def name(self):
        """
        The name of the object.
        """
        return self.__name

    def parent(self):
        """
        The parent MooseDocsNode object.
        """
        return self.__parent

    def root(self):
        """
        Returns the "root" node of this node.
        """
        def root_helper(node):
            if node.parent():
                return root_helper(node.parent())
            else:
                return node
        return root_helper(self)

    def source(self):
        """
        Return the source information.
        """
        return None

    def append(self, child):
        """
        Add a child node.
        """
        self.__children.append(child)

    def build(self, *args, **kwargs):
        """
        Main command that builds content, this is called from the build.py script.
        """
        pass

    def breadcrumbs(self):
        """
        Return a list of all the parent nodes.
        """
        crumbs = []
        def breadcrumb_helper(node):
            crumbs.insert(0, node)
            if node.parent():
                breadcrumb_helper(node.parent())
        breadcrumb_helper(self)
        return crumbs

    def relpath(self, path):
        """
        Returns the relative path to the supplied path compared to the current pages location.

        Args:
          path[str]: The path, with respect to the 'site_dir'.
        """
        if path.startswith('http'):
            return path
        return os.path.relpath(os.path.join(self.__site_dir, path), self.path())

    def path(self):
        """
        Return the current path based on the node location in the tree.
        """
        crumbs = [c.name() for c in self.breadcrumbs()]
        path = os.path.join(self.__site_dir, *crumbs)
        return path.rstrip('/')

    def url(self, *args, **kwargs):
        """
        Return the url to the page being created.
        """
        return None
