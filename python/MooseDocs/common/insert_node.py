def insert_node_before(node0, node1):
    """Insert node0 before node1."""
    _insert_node(node0, node1, 0)

def insert_node_after(node0, node1):
    """Insert node0 after node1)."""
    _insert_node(node0, node1, 1)

def _insert_node(node0, node1, offset):
    """Helper for inserting nodes."""
    parent = node1.parent
    children = list(node1.parent.children)
    for child in children:
        child.parent = None
    index = children.index(node1)
    children.insert(index+offset, node0)
    for child in children:
        child.parent = parent
