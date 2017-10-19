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
    REQUIRED_ATTRIBUTES = []

    def __init__(self, parent=None, name=None, **kwargs):
        anytree.NodeMixin.__init__(self)
        self.parent = parent
        self.name = name if name is not None else self.__class__.__name__
        self.__attributes = dict()
        for key, value in kwargs.iteritems():
            self[key] = value

        for key in self.REQUIRED_ATTRIBUTES:
            if key not in self:
                msg = "The key '{}' must be provided to the node {}".format(key, self.name)
                raise ValueError(msg)

    @property
    def attributes(self):
        """
        Return the attributes dict.
        """
        return self.__attributes

    def __contains__(self, key):
        """
        Allow "in" to be used for testing for attributes, this all tests that the attribute is
        not None.
        """
        return (key in self.__attributes) and (self.__attributes[key] is not None)

    def __setitem__(self, key, value):
        """
        Operator[] method for setting attribute.
        """
        key = key.rstrip('_')
        self.__attributes[key] = value

    def __getitem__(self, key):
        """
        Operator[] method for getting attribute.
        """
        try:
            return self.__attributes[key]
        except KeyError:
            LOG.error('Unknown attribute "%s" in node %s', key, self.name)

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
