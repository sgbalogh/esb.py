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

            zero_or_more = (rule_string[-1] == '*') # zero or more occurrence
            zero_or_one = (rule_string[-1] == '?') # zero or one occurrence

            rule_name = rule_string[:-1] if zero_or_more or zero_or_one else rule_string # take out the asterisk

            rule_node = RuleNode(val=rule_name, zero_or_one=zero_or_one, zero_or_more=zero_or_more, is_end=is_end)

            # if this node is not zero_or_more (while the next node is) and not last element
            if is_end and not (rule_node.zero_or_more or rule_node.zero_or_one):
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
    def __init__(self, val=None, next=None, zero_or_one=False, zero_or_more=False, is_end=False):
        self.value = val
        self.next = next
        self.zero_or_one = zero_or_one
        self.zero_or_more = zero_or_more
        self.is_end = is_end

    def __str__(self):
        return str(self.value)


class Rules:
    ignored_tags = [Tags.Token.START, Tags.Token.END]

    @staticmethod
    def get_siblings_rules():
        rules = []

        r = Rule('siblings_start', is_first=True)
        r.add_rule([Tags.Token.PERSON_NUMBER, "siblings_type", "siblings_name", "siblings_start*"])

        r2 = Rule('siblings_type')
        r2.add_rule([Tags.Token.PERSON_BROTHERS, Tags.Token.DELIMITER+"?"])
        r2.add_rule([Tags.Token.PERSON_SISTERS,  Tags.Token.DELIMITER+"?"])

        r3 = Rule('siblings_name')
        r3.add_rule([Tags.Token.PERSON_NAME, Tags.Token.META_PARENTHETICAL+"?", "siblings_location?", Tags.Token.DELIMITER+"?",
                     "siblings_name*"])

        r4 = Rule('siblings_location')
        r4.add_rule([Tags.Token.PERSON_LOCATED_IN, Tags.Token.LOCATION_NAME])

        rules.append(r)
        rules.append(r2)
        rules.append(r3)
        rules.append(r4)

        return rules

    @staticmethod
    def get_parent_rules():
        rules = []

        r = Rule('parent_start', is_first=True)
        r.add_rule(["parent_type", "parent_status?", "parent_location?", Tags.Token.PERSON_NAME+'?',
                    Tags.Token.DELIMITER+'?', 'parent_start*'])

        r2 = Rule('parent_type')
        r2.add_rule([Tags.Token.PERSON_FATHER])
        r2.add_rule([Tags.Token.PERSON_MOTHER])
        r2.add_rule([Tags.Token.PERSON_PARENTS])

        r3 = Rule('parent_location')
        r3.add_rule([Tags.Token.PERSON_LOCATED_IN, Tags.Token.LOCATION_NAME])

        r4 = Rule('parent_status')
        r4.add_rule([Tags.Token.PERSON_IS_DEAD])
        r4.add_rule([Tags.Token.PERSON_IS_LIVING])

        rules.append(r)
        rules.append(r2)
        rules.append(r3)
        rules.append(r4)

        return rules

    @staticmethod
    def get_emigration_rules():
        rules = []

        r = Rule('emigration_start', is_first=True)
        r.add_rule([Tags.Token.EMIGRATION_ARRIVED, Tags.Token.LOCATION_NAME+'?', 'emigration_date?',
                    Tags.Token.EMIGRATION_VIA, 'emigration_vessel'])

        r2 = Rule('emigration_date')
        r2.add_rule([Tags.Token.TIME_MONTH, Tags.Token.TIME_YEAR, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.TIME_MONTH, Tags.Token.TIME_DATE, Tags.Token.DELIMITER+'?'])

        r3 = Rule('emigration_vessel')
        r3.add_rule([Tags.Token.EMIGRATION_VESSEL, Tags.Token.EMIGRATION_VESSEL_HAS_ORIGIN+'?',
                     Tags.Token.LOCATION_NAME])

        rules.append(r)
        rules.append(r2)
        rules.append(r3)

        return rules

    @staticmethod
    def get_children_rules():
        rules = []

        r = Rule('children_start', is_first=True)
        r.add_rule([Tags.Token.PERSON_NUMBER, Tags.Token.PERSON_CHILDREN, Tags.Token.DELIMITER+'?', 'children_name*'])

        r2 = Rule('children_name')
        r2.add_rule([Tags.Token.PERSON_NAME, Tags.Token.DELIMITER+'?'])

        rules.append(r)
        rules.append(r2)

        return rules

    @staticmethod
    def get_spouse_rules():
        rules = []

        r = Rule('spouse_start', is_first=True)
        r.add_rule(['spouse_relation', Tags.Token.DELIMITER+'?', 'spouse_person*',
                    'spouse_start*'])

        r2 = Rule('spouse_person')
        r2.add_rule([Tags.Token.PERSON_NAME, Tags.Token.PERSON_IS_DEAD+'?', 'spouse_duration?', 'spouse_location?',
                     Tags.Token.DELIMITER+'?'])

        r3 = Rule('spouse_relation')
        r3.add_rule([Tags.Token.REL_HAS_HUSBAND])
        r3.add_rule([Tags.Token.REL_HAS_WIFE])
        r3.add_rule([Tags.Token.REL_HAS_SPOUSE])
        r3.add_rule([Tags.Token.REL_IS_WIDOW_OF])

        r4 = Rule('spouse_location')
        r4.add_rule([Tags.Token.PERSON_LOCATED_IN, Tags.Token.LOCATION_NAME])

        r5 = Rule('spouse_duration')
        r5.add_rule([Tags.Token.TIME_YEAR, Tags.Token.TIME_DURATION_YEAR])

        rules.append(r)
        rules.append(r2)
        rules.append(r3)
        rules.append(r4)
        rules.append(r5)

        return rules

    @staticmethod
    def get_record_ref_rules():
        rules = []

        r = Rule('ref_start', is_first=True)
        r.add_rule([Tags.Token.META_SEE, 'ref_account*', 'ref_start*'])
        r.add_rule([Tags.Token.META_IS_SAME_AS, 'ref_account*', 'ref_start*'])

        r2 = Rule('ref_account')
        r2.add_rule([Tags.Token.META_ACCOUNT_NUMBER, Tags.Token.DELIMITER+'?'])

        rules.append(r)
        rules.append(r2)

        return rules

    @staticmethod
    def get_age_rules():
        r = Rule('age_start', is_first=True)
        r.add_rule([Tags.Token.PERSON_AGE_YEAR, Tags.Token.PERSON_AGE])

        return [r]

    @staticmethod
    def get_bio_rules():
        r = Rule('bio_start', is_first=True)
        r.add_rule([Tags.Token.TIME_DURATION_VALUE, Tags.Token.TIME_DURATION_YEAR, Tags.Token.PERSON_LOCATED_IN,
                    Tags.Token.LOCATION_NAME])

        return [r]

    @staticmethod
    def get_marital_rules():
        r = Rule('marital_start', is_first=True)
        r.add_rule([Tags.Token.PERSON_IS_SINGLE])

        return [r]

    @staticmethod
    def get_native_of_rules():
        rules = []

        r = Rule('native_of_start', is_first=True)
        r.add_rule([Tags.Token.REL_IS_NATIVE_OF, Tags.Token.LOCATION_NAME, Tags.Token.DELIMITER+'?', 'native_of_dist?',
                    'native_of_start*'])

        r2 = Rule('native_of_dist')
        r2.add_rule([Tags.Token.LOCATION_DISTANCE, Tags.Token.LOCATION_DISTANCE_UNIT+'?', Tags.Token.LOCATION_FROM,
                     Tags.Token.LOCATION_NAME])

        rules.append(r)
        rules.append(r2)

        return rules

    @staticmethod
    def get_occupation_rules():
        r = Rule('occupation_start', is_first=True)
        r.add_rule([Tags.Token.WORK_WORKS_FOR, Tags.Token.WORK_EMPLOYER_NAME])
        r.add_rule([Tags.Token.WORK_OCCUPATION])

        return [r]

    @staticmethod
    def get_residential_rules():
        r = Rule('residential_start', is_first=True)
        r.add_rule([Tags.Token.RESIDENTIAL_LIVES_WITH, 'residential_person*', 'residential_start*'])
        r.add_rule([Tags.Token.RESIDENTIAL_LIVED_WITH, 'residential_person*', 'residential_start*'])
        r.add_rule([Tags.Token.RESIDENTIAL_CURRENTLY_LIVING_AT, Tags.Token.DELIMITER+'?', 'residential_location',
                    'residential_person*', 'residential_start*'])
        r.add_rule([Tags.Token.RESIDENTIAL_FORMERLY_LOCATED_AT, Tags.Token.DELIMITER+'?', 'residential_location',
                    'residential_person*', 'residential_start*'])

        r2 = Rule('residential_person')
        r2.add_rule([Tags.Token.PERSON_NAME, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_SON, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_MOTHER, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_FATHER, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_BROTHERS, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_SISTERS, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_WIFE, Tags.Token.DELIMITER+'?'])
        r2.add_rule([Tags.Token.PERSON_CHILDREN, Tags.Token.DELIMITER+'?'])

        r3 = Rule('residential_location')
        r3.add_rule([Tags.Token.LOCATION_NAME, Tags.Token.DELIMITER+'?'])

        return [r, r2, r3]

    @staticmethod
    def get_rules_by_tag(tag):

        if tag == Tags.Thematic.FAM_SIBLINGS:
            return Rules.get_siblings_rules()

        elif tag == Tags.Thematic.FAM_PARENTS:
            return Rules.get_parent_rules()

        elif tag == Tags.Thematic.SUBJ_EMIGRATION:
            return Rules.get_emigration_rules()

        elif tag == Tags.Thematic.FAM_CHILDREN:
            return Rules.get_children_rules()

        elif tag == Tags.Thematic.FAM_SPOUSE:
            return Rules.get_spouse_rules()

        elif tag == Tags.Thematic.META_RECORD:
            return Rules.get_record_ref_rules()

        elif tag == Tags.Thematic.SUBJ_AGE:
            return Rules.get_age_rules()

        elif tag == Tags.Thematic.SUBJ_BIO:
            return Rules.get_bio_rules()

        elif tag == Tags.Thematic.SUBJ_MARTIAL:
            return Rules.get_marital_rules()

        elif tag == Tags.Thematic.SUBJ_NATIVEOF:
            return Rules.get_native_of_rules()

        elif tag == Tags.Thematic.SUBJ_OCCUPATION:
            return Rules.get_occupation_rules()

        elif tag == Tags.Thematic.SUBJ_RESIDENCE:
            return Rules.get_residential_rules()

        else:
            return []

    @staticmethod
    # return <next index after last matching character, rule_name> or -1 if nothing
    def check_match_rule(rules, tokens, start_idx):
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

                label_set = set() # check if zero_or_one nodes have occurred more than once

                while idx < len(tokens) and node is not None:

                    # check zero_or_one elements if they occur more than once
                    if node.zero_or_one:
                        if node.value not in label_set:
                            label_set.add(node.value)
                        else:
                            # repeat occurrence of zero_or_one element
                            break

                    # if rule node and token are matched, continue to match
                    if node.value == tokens[idx]:

                        if node.zero_or_more:
                            # matches multiple of same node if zero_or_more
                            while idx < len(tokens) and node.value == tokens[idx]:
                                idx += 1

                        else:
                            idx += 1

                        node = node.next

                    elif node.zero_or_one or node.zero_or_more: # skip if allow zero of this node
                        node = node.next

                    else:
                        break

                # if it reached end of loop or found matching before end of string
                if (node is None or node.is_end) and start_node.value == tokens[start_idx]:
                    return idx, rule

        return -1, None

    @staticmethod
    def parse_tree_by_label(rules, tokens, remarks, nodes):
        if len(tokens) == 0 or len(remarks) == 0:
            return

        output_tokens = copy(tokens)
        output_remarks = copy(remarks)
        output_nodes = copy(nodes)

        for idx in range(len(output_tokens)-1, -1, -1):

            next_idx, matched_rule = Rules.check_match_rule(rules, output_tokens, idx)

            if matched_rule is not None:

                parent_node = TreeNode(matched_rule.name)

                # add child nodes to current node
                for node_idx in range(idx, next_idx):
                    parent_node.children.append(output_nodes[node_idx])

                output_tokens = output_tokens[:idx] + [matched_rule.name] + output_tokens[next_idx:]
                output_remarks = output_remarks[:idx] + ['N/A'] + output_remarks[next_idx:]
                output_nodes = output_nodes[:idx] + [parent_node] + output_nodes[next_idx:]

        return output_tokens, output_remarks, output_nodes






