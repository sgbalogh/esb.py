# vertex / node as named entity
# edge as attribute/property


class TreeNode(object):

    def __init__(self, label, token=None):
        self.label = label
        self.token = token
        self.children = []
        self.dfs_color = "white"
        self.dfs_parent = None

    def __str__(self):
        return '[{}, {}]'.format(self.label, self.token)

    @staticmethod
    def preorder_print(node):
        if node is None:
            return
        print('{}'.format(node))
        for child in node.children:
            TreeNode.preorder_print(child)
