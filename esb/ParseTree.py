# vertex / node as named entity
# edge as attribute/property



class TreeNode(object):
    def __init__(self, val):
        self._value = val
        self._children = [] # tuple (value, edge)

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, child, label):
        self._children.append((child, TreeEdge(label, self, child)))


class TreeEdge(object):
    def __init__(self, attribute=None, start_node=None, end_node=None):
        self._attribute = attribute
        self._start_node = start_node
        self._end_node = end_node