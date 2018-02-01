import os
import anytree
import hit
import message

class HitNode(anytree.NodeMixin):
    """
    An anytree.Node object for building a hit tree.
    """
    def __init__(self, name='', parent=None):
        super(HitNode, self).__init__()
        self.name = name           # anytree.Node property
        self.parent = parent       # anytree.Node property
        self.__parameters = dict() # HitNode property

    @property
    def parameters(self):
        """
        Access to the parameters dict() for this node.
        """
        return self.__parameters

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
        return self.__parameters[param]

    def __repr__(self):
        """
        Dislpay the node name and parameters.
        """
        if self.parameters:
            return '{}: {}'.format(self.name, repr(self.parameters))
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

    root = HitNode()
    hit_node = hit.parse(filename, content)
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
            new = HitNode(hit_child.path(), parent=root)
            _hit_parse(new, hit_child, filename)
        elif hit_child.type() == hit.NodeType.Field:
            root.parameters[hit_child.path()] = hit_child.param()
    return root

if __name__ == '__main__':
    filename = '/Users/slauae/projects/moose/test/tests/kernels/simple_diffusion/simple_diffusion.i'
    root = hit_load(filename)
    print root
