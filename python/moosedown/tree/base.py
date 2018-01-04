import copy
import logging
import weakref
import inspect
import anytree

LOG = logging.getLogger(__name__)

class Property(object):
    """
    A descriptor object for creating properties for the NodeBase class defined below.

    A system using this object and the NodeBase class was created to allow for dynamic property
    creation on nodes that allows defaults, types, and a required status to be defined for the
    properties.

    When developing the tokens it was desirable to create properties (via @property) etc. to
    access token data, but it became a bit tedious so an automatic method was created, see
    the documentation on the NodeBase class for information on using the automatic system.

    This property class can also be inherited from to allow for arbitrary checks to be performed,
    for example that a number is positive or a list is the correct length.
    """
    def __init__(self, name, default=None, ptype=None, required=False):
        self.name = name
        self.__type = ptype
        self.__required = required
        self.__default = default

        if (ptype is not None) and (not isinstance(ptype, type)):
            msg = "The supplied property type (ptype) must be of type 'type', but '{}' provided."
            raise TypeError(msg.format(type(ptype).__name__))

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
            msg = "The supplied property '{}' must be of type '{}', but '{}' was provided."
            raise TypeError(msg.format(self.name, self.type.__name__, type(value).__name__))
        instance._NodeBase__properties[self.name] = value

    def __get__(self, instance, key):
        """Get the property value."""
        return instance._NodeBase__properties.get(self.name, self.default)

class NodeBase(anytree.NodeMixin):
    """
    Base class for tree nodes that accepts defined properties and arbitrary attributes.

    Well defined properties may be created using the class PROPERTIES variable. For example,

        class ExampleNode(NodeBase):
            PROPERTIES = Property('foo', required=True)

        node = ExampleNode(foo=42)
        node.foo = 43

    Additionally, arbitrary attributes can be stored on creation or by using the dict() style
    set/get methods. By convention any leading or trailing underscores used in defining the
    attribute in the constructor are removed for storage.

        node = ExampleNode(foo=42, class_='fancy')
        node['class'] = 'not fancy'


    Inputs:
        parent[NodeBase]: (Optional) Set the parent node of the node being created, if not
                          supplied the resulting node will be the root node.
        kwargs: (Optional) Any key, value pairs supplied are stored as properties or attributes.
    """
    PROPERTIES = [] # this gets set by the @properties decorator

    def __init__(self, parent=None, name=None, **kwargs) :
        anytree.NodeMixin.__init__(self)

        # TODO: This fails for some reason
        # Check parent type
        #if (parent is not None) and (not isinstance(parent, NodeBase)):
        #    msg = "The supplied parent must be a NodeBase object, but '{}' was provided."
        #    raise TypeError(msg.format(type(parent).__name__))

        self.parent = parent
        self.name = name if name is not None else self.__class__.__name__
        self.__properties = dict() # storage for property values
        self.__attributes = dict() # storage for attributes (i.e., unknown key, values)

        # Check PROPERTIES type
        if not isinstance(self.PROPERTIES, list):
            raise TypeError("The class attribute 'PROPERTIES' must be a list.")

        # Apply the default values
        for prop in self.PROPERTIES:
            if not isinstance(prop, Property):
                msg = "The supplied property must be a Property object, but {} provided."
                raise TypeError(msg.format(type(prop).__name__))

            # TODO: this can't work because properties are class methods
            """
            if hasattr(self, prop.name):
                msg = "The supplied property '{}' is already a defined property on the {} object."
                raise TypeError(msg.format(prop.name, type(self).__name__))
            """
            setattr(self.__class__, prop.name, prop)
            self.__properties[prop.name] = prop.default

        # Update the properties from the key value pairs
        for key, value in kwargs.iteritems():
            if value is None:
                continue
            if key in self.__properties:
                setattr(self, key, value)
            else:
                self.__attributes[key.strip('_')] = value

        # Check required
        for prop in self.PROPERTIES:
            if prop.required and self.__properties[prop.name] is None:
                raise IOError("The property '{}' is required.".format(prop.name))

    def __repr__(self):
        """
        Prints the name of the token, this works in union with __str__ to print
        the tree structure of any given node.
        """
        return '{}: {}'.format(self.name, repr(self.__properties))

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

    def __getitem__(self, key):
        """
        Return an attribute.
        """
        return self.__attributes[key]

    def __setitem__(self, key, value):
        """
        Create/set an attribute.
        """
        self.__attributes[key] = value

    def get(self, key, default):
        """
        Get an attribute with a possible default.
        """
        value = self.__attributes.get(key, default)
        if value is None:
            value = default
        return default

    @property
    def attributes(self):
        """
        Return the attributes for the object.
        """
        return self.__attributes

    def __contains__(self, key):
        """
        Test if attribute exists within "in" keyword.
        """
        return key in self.__attributes

    def write(self):
        """
        Abstract method for outputting content of node to a string.
        """
        out = ''
        for child in self.children:
            out += child.write()
        return out

    def get_root(self):
        if self.parent:
            return self._path[0]
        else:
            return self

    def find(self, name, maxlevel=None):
        """
        Search for a node, by name.
        """
        for node in anytree.PreOrderIter(self, maxlevel=maxlevel):
            if node.name == name:
                return node
