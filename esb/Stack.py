import copy

class Stack(object):
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)

    def clone(self):
        return copy.deepcopy(self)

    def clear(self):
        self.items = []

    def __str__(self):
        return str(self.items)