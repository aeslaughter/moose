import logging
import anytree

LOG = logging.getLogger(__name__)

class Property(object):
    """
    Descriptor for creating dynamic, type-checked properties for node classes to avoid
    creating endless setters and getters.
    """
    def __init__(self, key, default=None, ptype=None):
        self.__key = key

        if (default is not None) and (ptype is not None) and (not isinstance(default, ptype)):
            raise TypeError("The supplied property value must be of type '{}', but '{}' was"
                            "provided.".format(ptype.__name__, type(default).__name__))

        self.__default = default
        self.__type = ptype

    def __set__(self, ins, key, value):
        if (self.__type is not None) and (not isinstance(value, self.__type)):
            raise TypeError("The supplied property value must be of type '{}', but '{}' was"
                            "provided.".format(self.__type.__name__, type(value).__name__))
        ins[key] = value

    def __get__(self, ins, key):
        return ins.get(key, self.__default)

    @property
    def key(self):
        return self.__key

    @property
    def default(self):
        return self.__default

    @property
    def type(self):
        return self.__type


class NodeBase(anytree.NodeMixin):
    """
    Base class for tree nodes that accepts arbitrary attributes.

    Inputs:
        parent[NodeBase]: (Optional) Set the parent node of the node being created, if not
                          supplied the resulting node will be the root node.
        kwargs: (Optional) Any key, value pairs supplied are stored in the settings property
                and may be retrieved via the various access methods.
    """
    PROPERTIES = []
    REQUIRED_ATTRIBUTES = []

    def __init__(self, parent=None, name=None, **kwargs):
        anytree.NodeMixin.__init__(self)
        self.parent = parent
        self.name = name if name is not None else self.__class__.__name__
        self.__attributes = dict()

        # Add properties
        if not isinstance(self.PROPERTIES, list):
            raise TypeError("The PROPERTIES class attribute must be a list.")
        for prop in self.PROPERTIES:
            if not isinstance(prop, Property):
                raise TypeError("The supplied property must of type Property.")
            setattr(self, prop.key, prop)

        # Insert key, value pairs from constructor
        for key, value in kwargs.iteritems():
            self[key] = value

        # Check for required attributesg
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

    def get(self, key, default):
        """
        Method for getting attribute given a default.
        """
        return self.__attributes.get(key, default)

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
        return '{}: {}'.format(self.name, repr(self.attributes))

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
