from esb.Tags import Tags
from esb.Stack import Stack
from esb.ParseTree import *
from copy import copy

# list of linkedlist heads
class Rule:
    def __init__(self, name, is_first=False):
        self.name = name
        self.start_nodes = list()
        self.is_first = is_first

    def add_rule(self, rule_strings):

        head = RuleNode('start')
        current = head

        stack = Stack()
        is_end = True # reached end of rule node

        # starting from last element of string to first
        for rule_string in reversed(rule_strings):
            zero_or_more = (rule_string[-1] == '*')
            rule_name = rule_string[:-1] if zero_or_more else rule_string # take out the asterisk

            rule_node = RuleNode(val=rule_name, zero_or_more=zero_or_more, is_end=is_end)

            # if this node is not zero_or_more (while the next node is) and not last element
            if is_end and not rule_node.zero_or_more:
                is_end = False

            stack.push(rule_node)



        # push every rule into stack
        while not stack.is_empty():
            # change to next node
            current.next = stack.pop()
            current = current.next

        self.start_nodes.append(head.next)

    def __str__(self):
        return self.name

# linkedlist node
class RuleNode(object):
    def __init__(self, val=None, prev=None, next=None, zero_or_more=False, is_end=False):
        self.value = val
        self.next = next
        self.prev = prev
        self.zero_or_more = zero_or_more
        self.is_end = is_end

    def __str__(self):
        return str(self.value)


class Rules:

    @staticmethod
    def get_siblings_rules():
        rules = []

        r = Rule('siblings_start', is_first=True)
        r.add_rule([Tags.Token.PERSON_NUMBER, "siblings_type", "siblings_name", "siblings_start*"])

        r2 = Rule('siblings_type')
        r2.add_rule([Tags.Token.PERSON_BROTHERS, "delimiter*"])
        r2.add_rule([Tags.Token.PERSON_SISTERS, "delimiter*"])

        r3 = Rule('siblings_name')
        r3.add_rule([Tags.Token.PERSON_NAME, "siblings_meta*", "siblings_location*", "delimiter*", "siblings_name*"])

        r4 = Rule('siblings_location')
        r4.add_rule([Tags.Token.PERSON_LOCATED_IN, Tags.Token.LOCATION_NAME])

        r5 = Rule('delimiter')
        r5.add_rule([Tags.Token.DELIMITER])

        r6 = Rule('siblings_meta')
        r6.add_rule([Tags.Token.META_PARENTHETICAL])

        rules.append(r)
        rules.append(r2)
        rules.append(r3)
        rules.append(r4)
        rules.append(r5)
        rules.append(r6)

        return r, rules


    @staticmethod
    def check_match_rule(rules, tokens, start_idx): # return <next index after last matching character, rule_name> or -1 if nothing
        if len(tokens) == 0:
            return -1, None

        # check every rule
        for rule in rules:

            # check every starting node in this rule
            for node in rule.start_nodes:

                if node.value != tokens[start_idx]:
                    continue

                start_node = node
                idx = start_idx

                while idx < len(tokens) and node is not None:

                    # if rule node and token are matched, continue to match
                    if node.value == tokens[idx]:
                        node = node.next
                        idx += 1

                    elif node.is_end:
                        node = node.next
                    else:
                        break

                # if it reached end of loop or found matching before end of string
                if (node is None or node.is_end) and start_node.value == tokens[start_idx]:
                    return idx, rule

        return -1, None

    @staticmethod
    def brute_force(rules, labels, nodes):
        if len(labels) == 0:
            return

        output_labels = copy(labels)
        output_nodes = copy(nodes)

        for idx in range(len(output_labels)-1, -1, -1):
            current_label = output_labels[idx]

            next_idx, matched_rule = Rules.check_match_rule(rules, output_labels, idx)

            if matched_rule is not None:

                parent_node = TreeNode(matched_rule.name)

                # add child nodes to current node
                for node_idx in range(idx, next_idx):
                    parent_node.children.append(output_nodes[node_idx])

                output_labels = output_labels[:idx] + [matched_rule.name] + output_labels[next_idx:]
                output_nodes = output_nodes[:idx] + [parent_node] + output_nodes[next_idx:]

        return output_labels, output_nodes






