"""
Sorted container for storing objects.
"""

class Storage(object):
    """
    Container for storing objects by name with the ability to insert relative to existing objects.

    Inputs:
      s_type: The type of object to store, this is provided for error checking.
    """
    def __init__(self, stype=None):

        # The type of Element allowed to be stored
        self._type = stype

        # The names of the objects as assigned when added
        self._keys = []

        # The objects being stored, a list is used for fast looping, consequently
        self._objects = []

    def add(self, key, obj, location='_end'):
        """
        Adds the 'obj' class with the given name to the storage container.

        Args:
            key[str]: The name of the object being added
            obj[stype]: The object to store, where stype is defined in constructor (see constructor)
            location[int]: The integer location to insert the item
            location[str]: The name of the key where this should be inserted, it is possible to pass
                           special locations:
                               '_end': Insert the key being added to the end of the container
                               '_begin': Insert the key being added to the beginning of container
                               '<key': Insert the new key before the key given with the '<' prefix
                               '>key': Insert the new key after the key given with the '<' prefix
                               'key': Insert the new key after the key (same as '<' prefix)
        """

        # Check the type
        if not isinstance(obj, self._type):
            msg = 'Incorrect object provided, expected {} but received {}'
            msg = msg.format(self._type.__name__, type(obj).__name__)
            raise TypeError(msg)

        # Check if key exists
        if key in self._keys:
            raise ValueError("The key '{}' already exists.".format(key))

        # Determine the index
        index = None
        if isinstance(location, str):
            if location == '_end':
                index = len(self._keys)
            elif location == '_begin':
                index = 0
            elif location.startswith('<'):
                index = self._keys.index(location[1:])
            elif location.startswith('>'):
                index = self._keys.index(location[1:]) + 1
            else:
                index = self._keys.index(location)
        elif isinstance(location, int):
            index = location
        else:
            raise TypeError("The supplied input must be of the 'str' or 'int'.")

        self._keys.insert(index, key)
        self._objects.insert(index, obj)

    def __getitem__(self, key):
        """
        Return class type by key.
        """
        if isinstance(key, int):
            index = key
        elif isinstance(key, str):
            index = self._keys.index(key)
        else:
            raise TypeError("The supplied type must be 'int' or 'str' but {} given." \
                            .format(type(key).__name__))

        return self._objects[index]

    def __contains__(self, key):
        """
        Check if key, index is valid.
        """
        if isinstance(key, int):
            return key < len(self._keys)
        elif isinstance(key, str):
            return key in self._keys

        raise TypeError("The supplied type must be 'int' or 'str' but {} given." \
                        .format(type(key).__name__))

    def __iter__(self):
        """
        Enables iteration over the Element classes stored in this container.
        """
        for obj in self._objects:
            yield obj

    def __len__(self):
        """
        Return the number of items stored.
        """
        return len(self._keys)
