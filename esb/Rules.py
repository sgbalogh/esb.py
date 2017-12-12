from esb.Tags import Tags
from esb.Stack import Stack

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
            current.next = stack.pop()
            current = current.next

        self.start_nodes.append(head.next)

    def __str__(self):
        return self.name

# linkedlist node
class RuleNode(object):
    def __init__(self, val=None, next=None, zero_or_more=False, is_end=False):
        self.value = val
        self.next = next
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
        r5.add_rule([","])
        r5.add_rule(["&"])

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
    def shift_reduce(rules, start_rule, src_stack):
        if src_stack.size() == 0:
            return

        stack = src_stack.clone()

        for rule in rules:
            if rule == start_rule: # skip first_rule. only used for final check
                continue

            # TODO: check first element of each rule, see if anyone of them match. If the element is another rule_name, recursive this.
            for node in rule.start_nodes:
                # check if rule is matched with string
                if node.value == stack.peek() and node.is_end:
                    _ = stack.pop()
                    stack.push(rule.name)


        # TODO: match with first_rule_name
        nodes = stack.items

        for starting_node in start_rule.start_nodes:
            idx = 0
            current = starting_node

            while current is not None and idx < len(nodes):
                if current.value != nodes[idx] and not current.zero_or_more:
                    break

                current = current.next
                idx += 1

            if current is None and idx == len(nodes):
                stack.clear()
                stack.push(start_rule)


        return stack







