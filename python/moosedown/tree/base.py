import copy
import logging
import anytree

LOG = logging.getLogger(__name__)

class Property(object):
    """
    A helper object for creating attributes for the NodeBase class defined below.

    A system using this object and the NodeBase class was created to allow for dynamic attribute
    access to properties on nodes that allows defaults, types, and a required status to be
    defined for the properties.

    When developing the tokens it was desirable to create properties (via @property) etc. to
    access token data, but it became a bit tedious so an automatic method was created, see
    the documentation on the NodeBase class for information on using the automatic system.
    """
    def __init__(self, name, default=None, ptype=None, required=False):
        self.__name = name
        self.__type = ptype
        self.__required = required
        self.__value = None
        self.value = default # use the setter to type checking occurs

    @property
    def name(self):
        """The property name."""
        return self.__name

    @property
    def value(self):
        """The property value."""
        return self.__value

    @value.setter
    def value(self, value):
        """Type checking setter for the property value."""
        if (self.__type is not None) and (not isinstance(value, self.__type)):
            msg = "The supplied property '{}' must be of type '{}', but '{}' was provided."
            raise TypeError(msg.format(self.name, self.type.__name__, type(value).__name__))
        self.__value = value

    @property
    def type(self):
        """The required property type."""
        return self.__type

    @property
    def required(self):
        """Return the required status for the property."""
        return self.__required

class NodeBase(anytree.NodeMixin):
    """
    Base class for tree nodes that accepts defined properties.

    Inputs:
        parent[NodeBase]: (Optional) Set the parent node of the node being created, if not
                          supplied the resulting node will be the root node.
        kwargs: (Optional) Any key, value pairs supplied are stored in the settings property
                and may be retrieved via the various access methods.
    """
    PROPERTIES = []

    def __init__(self, parent=None, name=None, **kwargs):
        anytree.NodeMixin.__init__(self)
        self.__properties = dict()
        self.parent = parent
        self.name = name if name is not None else self.__class__.__name__

        # Check the type of the class variable PROPERTIES
        if not isinstance(self.PROPERTIES, list):
            raise TypeError("The PROPERTIES class attribute must be a list.")

        for prop in self.PROPERTIES:
            if not isinstance(prop, Property):
                msg = "The supplied property '{}' must of type Property."
                raise TypeError(msg.format(prop.name))
            if prop.required and prop.value is None:
                msg = "The supplied property '{}' must be supplied a value."
                raise TypeError(msg.format(prop.name))
            self.__properties[prop.name] = copy.copy(prop) # create a new Property instance

    def __getattr__(self, key):
        if key in self.__properties:
            return self.__properties[key].value

    def __setattr__(self, key, value):
        if hasattr(self, '__properties') and (key in self.__properties):
            prop = self.__properties[key]
            prop.value = value
        else:
            super(NodeBase, self).__setattr__(key, value)


    #@property
    #def attributes(self):
    #    """
    #    Return the attributes dict.
    #    """
    #    return self.__attributes

    def __contains__(self, key):
        """
        Allow "in" to be used for testing for attributes, this all tests that the attribute is
        not None.
        """
        return (key in self.attributes) and (self.attributes[key] is not None)

    #def __setitem__(self, key, value):
    #    """
    #    Operator[] method for setting attribute.
    #    """
    #    try:
    #        key = key.rstrip('_')
    #        attr = getattr(self, key)
    #        attr = value
    #    except:
    #        raise KeyError('Unknown attribute "{}" in node {}'.format(key, self.name))

    #def get(self, key, default):
    #    """
    #    Method for getting attribute given a default.
    #    """
    #    return self.__attributes.get(key, default)

    #def __getitem__(self, key):
    #    """
    #    Operator[] method for getting attribute.
    #    """
    #    try:
    #        return self.__attributes[key]
    #    except KeyError:
    #        LOG.error('Unknown attribute "%s" in node %s', key, self.name)

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
