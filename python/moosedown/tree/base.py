import logging
import anytree

LOG = logging.getLogger(__name__)

class NodeBase(anytree.NodeMixin):
    """
    Base class for tree nodes that accepts arbitrary attributes.

    Inputs:
        parent[NodeBase]: (Optional) Set the parent node of the node being created, if not
                          supplied the resulting node will be the root node.
        kwargs: (Optional) Any key, value pairs supplied are stored in the settings property
                and may be retrieved via the various access methods.
    """
    def __init__(self, parent=None, **kwargs):
        anytree.NodeMixin.__init__(self)
        self.parent = parent
        self.__attributes = dict()
        for key, value in kwargs.iteritems():
            self[key] = value

    @property
    def attributes(self):
        """
        Return the attributes dict.
        """
        return self.__attributes

    def __setitem__(self, key, value):
        key = key.rstrip('_')
        self.__attributes[key] = value

    def __getitem__(self, key):
        try:
            return self.__attributes[key]
        except KeyError:
            LOG.error('Unknown attribute "%s" in node.', key)

    def __repr__(self):
        """
        Prints the name of the token, this works in union with __str__ to print
        the tree structure of any given node.
        """
        return self.name

    def __str__(self):
        """
        Print the complete tree beginning at this node.
        """
        return str(anytree.RenderTree(self))

    def __call__(self, index):
        """
        Return a child given the numeric index.

        Inputs:
            index[int]: The numeric index of the child object to return, this is the same
                        as doing self.children[index].
        """
        if len(self.children) <= index:
            LOG.error('A child node with index %d does not exist, there are %d children.',
                      index, len(self.children))
            return None
        return self.children[index]

    def __iter__(self):
        """
        Allows for iterator access over the child nodes.
        """
        for child in self.children:
            yield child

    def write(self):
        """
        Abstract method for outputting content of node to a string.
        """
        raise NotImplementedError("The write() method is not implemented.")
