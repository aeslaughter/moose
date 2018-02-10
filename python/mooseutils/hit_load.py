"""Wrapper for hit parser."""
import os
import anytree
import hit
import message

class HitNode(anytree.NodeMixin):
    """
    An anytree.Node object for building a hit tree.

    TODO: Store parameters as hit.Node and create a new node with __setitem__
    TODO: Remove parameters property
    """
    def __init__(self, name='', parent=None, line=None, hitnode=None):
        super(HitNode, self).__init__()
        self.name = name           # anytree.Node property
        self.parent = parent       # anytree.Node property
        self.__parameters = dict() # HitNode property
        self.__line = line
        self.__hitnode = hitnode   # hit.Node object

    #@property
    #def parameters(self):
    #    """
    #    Access to the parameters dict() for this node.
    #    """
    #    return self.__parameters

    @property
    def line(self):
        """
        Access to the line number.
        """
        return self.__line

    @property
    def fullpath(self):
        """
        Return the node full path.
        """
        out = []
        node = self
        while (node is not None):
            out.append(node.name)
            node = node.parent
        return '/'.join(out)

    def find(self, name, fuzzy=True):
        """
        Locate first occurance of a node by name starting from this node.

        Inputs:
            name[str]: The name to search for within the tree.
            fuzzy[bool]: When True (the default) a "fuzzy" search is performed, meaning
                         that the provide name must be in the node name. If
                         this is set to True the names must match exact.
        """
        for node in anytree.PreOrderIter(self):
            if (fuzzy and name in node.name) or (not fuzzy and name == node.name):
                return node

    def findall(self, name, fuzzy=True):
        """
        Locate all nodes withing the tree starting from this node.

        Inputs:
            name[str]: The name to search for within the tree.
            fuzzy[bool]: When True (the default) a "fuzzy" search is performed, meaning
                         that the provide name must be in the node name. If
                         this is set to True the names must match exact.
        """
        filter_ = lambda n: (fuzzy and name in n.name) or (not fuzzy and n.name == name)
        return [node for node in anytree.PreOrderIter(self, filter_=filter_)]

    def addParameter(self, *args):
        """
        Add a parameter to the node. There are two options for this method.

        addParameter(name, value)
        addParameter(field)

        Inputs:
            name[str]: The name for the paramter to add.
            value[int|float|bool|str]: The value for the parameter.

            field[hit.NodeType]: The hit node to add directly.

        """
        if len(args) == 1:
            self.__parameters[args[0].path()] = args[0]
        elif len(args) == 2:
            name = args[0]
            value = args[1]
            if isinstance(value, int):
                field_type = hit.FieldKind.Int
            elif isinstance(value, float):
                field_type = hit.FieldKind.Float
            elif isinstance(value, bool):
                field_type = hit.FieldKind.Bool
            else:
                field_type = hit.FieldKind.String
                value = str(value)

            child = hit.NewField(name, field_type, value)
            self.__hitnode.addChild(child)
            self.__parameters[name] = child

    def render(self):
        """
        Render the tree with the hit library.
        """
        return self.__hitnode.render()

    def __contains__(self, param):
        """
        Provides operator in access to the parameters of this node.

            if 'foo' in param:
                ...
        """
        return param in self.__parameters

    def __iter__(self):
        """
        Provides simple looping over children.

            for child in node:
                ...
        """
        for child in self.children:
            yield child

    def __getitem__(self, param):
        """
        Provides operator [] access to the parameters of this node.
        """
        return self.__parameters[param].param()

    def __setitem__(self, param, value):
        """
        Provides operator [] access to the parameters of this node.
        """
        return self.__parameters[param].setVal(value)

    def __repr__(self):
        """
        Dislpay the node name and parameters.
        """
        if self.__parameters:
            params = {k:v.param() for k,v in self.__parameters.iteritems()}
            return '{}: {}'.format(self.name, repr(params))
        return self.name

    def __str__(self):
        """
        Print the complete tree beginning at this node.
        """
        return str(anytree.RenderTree(self))

def hit_load(filename):
    """
    Read and parse a hit file (MOOSE input file format).

    Inputs:
        filenae[str]: The filename to open and parse.

    Returns a HitNode object, which is the root of the tree. HitNode objects are custom
    versions of the anytree.Node objects.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as fid:
            content = fid.read()
    else:
        message.mooseError("Unable to load the hit file ", filename)

    hit_node = hit.parse(filename, content)
    root = HitNode(hitnode=hit_node)
    _hit_parse(root, hit_node, filename)
    return root

def _hit_parse(root, hit_node, filename):
    """
    Parse the supplied content into a hit tree.

    Inputs:
        root[HitNode]: The HitNode object that the raw hit content will be inserted
        content[str]: The raw hit content to parse.
        filename[str]: (optional) The filename for error reporting.

    Returns a HitNode object, which is the root of the tree. HitNode objects are custom
    versions of the anytree.Node objects.
    """
    for hit_child in hit_node.children():
        if hit_child.type() == hit.NodeType.Section:
            new = HitNode(hit_child.path(), parent=root, line=hit_child.line(), hitnode=hit_child)
            _hit_parse(new, hit_child, filename)
        elif hit_child.type() == hit.NodeType.Field:
            root.addParameter(hit_child)
    return root

if __name__ == '__main__':
    filename = '../../test/tests/kernels/simple_diffusion/simple_diffusion.i'
    root = hit_load(filename)
    print root
