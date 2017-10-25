import copy
import logging
import weakref
import inspect
import anytree

LOG = logging.getLogger(__name__)



class properties(object):
    def __init__(self, *props):
        self._props = props

    def __call__(self, cls):
        decorator_self = self
        def wrapper(*args, **kwargs):
            for prop in self._props:
                setattr(cls, prop.name, prop)
            return cls(*args, **kwargs)
        return wrapper

class Property(object):
    """
    A descriptor object for creating attributes for the NodeBase class defined below.
    (http://nbviewer.jupyter.org/urls/gist.github.com/ChrisBeaumont/5758381/raw/descriptor_writeup.ipynb)

    A system using this object and the NodeBase class was created to allow for dynamic attribute
    access to properties on nodes that allows defaults, types, and a required status to be
    defined for the properties.

    When developing the tokens it was desirable to create properties (via @property) etc. to
    access token data, but it became a bit tedious so an automatic method was created, see
    the documentation on the NodeBase class for information on using the automatic system.
    """
    def __init__(self, name, default=None, ptype=None, required=False):
        self.name = name
        self.__type = ptype
        self.__required = required
        self.__default = default

        if (ptype is not None) and (default is not None) and (not isinstance(default, ptype)):
            msg = "The default for property must be of type '{}', but '{}' was provided."
            raise TypeError(msg.format(ptype.__name__, type(default).__name__))

    @property
    def default(self):
        return self.__default

    @property
    def type(self):
        """The required property type."""
        return self.__type

    @property
    def required(self):
        """Return the required status for the property."""
        return self.__required

    def __set__(self, instance, value):
        """Set the property value."""
        if (self.__type is not None) and (not isinstance(value, self.__type)):
            msg = "The supplied property must be of type '{}', but '{}' was provided."
            raise TypeError(msg.format(self.type.__name__, type(value).__name__))
        instance.attributes[self.name] = value

    def __get__(self, instance, key):
        """Get the property value."""
        return instance.attributes.get(self.name, self.default)

class NodeBase(anytree.NodeMixin):
    """
    Base class for tree nodes that accepts defined properties via a class attribute.

    Example:

        class ExampleNode(NodeBase):
            foo = Property(required=True)

        node = ExampleNode(foo=42)
        node.foo = 43

    Inputs:
        parent[NodeBase]: (Optional) Set the parent node of the node being created, if not
                          supplied the resulting node will be the root node.
        kwargs: (Optional) Any key, value pairs supplied are stored as attributes.
    """

    def __init__(self, parent=None, name=None, **kwargs):
        anytree.NodeMixin.__init__(self)
        self.parent = parent
        self.name = name if name is not None else self.__class__.__name__
        self.attributes = dict()

    def __contains__(self, key):
        """
        Allow "in" to be used for testing for attributes, this all tests that the attribute is
        not None.
        """
        return (key in self.__propertyies) and (self.__properties[key].value is not None)

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
