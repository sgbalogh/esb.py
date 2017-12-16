from esb import ParseTree
from esb import Rules
from esb.Triple import Triple
from dateutil import parser as dp

class SequenceParser:

    @staticmethod
    def discretize_tree(parse_tree):
        results = {}
        for theme in parse_tree.children:
            if theme.label == "fam:parents":
                results['parents'] = SequenceParser.discretize_parents(theme)
            elif theme.label == "subj:emigration-event":
                results['emigration'] = SequenceParser.discretize_emigration(theme)
            elif theme.label == "fam:siblings":
                continue
            elif theme.label == "meta:record-reference":
                results['references'] = SequenceParser.discretize_references(theme)
            elif theme.label == "subj:native-of":
                results['nativity'] = SequenceParser.discretize_nativity(theme)
        return results

    @staticmethod
    ## this methods seems to work; it's the only one using DFS at the moment
    def discretize_references(root_node):
        if root_node.label == "meta:record-reference":
            return SequenceParser.dfs(root_node, "t:meta:ACCOUNT_NUMBER")

    @staticmethod
    def dfs(root_node, search_label):
        results = []
        for x in root_node.children:
            results = results + SequenceParser.dfs_visit(x, search_label)
        return results

    @staticmethod
    def dfs_visit(start_node, search_label):
        to_return = []
        start_node.dfs_color = "gray"
        for x in start_node.children:
            if x.dfs_color == "white":
                x.dfs_parent = start_node
                if x.label == search_label:
                    to_return.append(x.token)
                else:
                    to_return = to_return + SequenceParser.dfs_visit(x, search_label)
        start_node.dfs_color = "black"
        return to_return



    @staticmethod
    ## unclear if this method is achieving 100% recall of parse trees
    def discretize_nativity(root_node):
        if root_node.label == "subj:native-of":
            record = {

            }
            for child in root_node.children:
                if child.label == "native_of_start":
                    for grandchild in child.children:
                        if grandchild.label == "t:location:NAME":
                            record['name'] = grandchild.token
            return [record]

    @staticmethod
    ## this method is NOT reading parse trees with 100% recall (see records[1174])
    def discretize_emigration(root_node):
        if root_node.label == "subj:emigration-event":
            record = {
                "date" : {},
                "vessel" : {}
            }
            for child in root_node.children:
                if child.label == "emigration_start":
                    for grandchild in child.children:
                        if grandchild.label == "emigration_date":
                            for greatgrandchild in grandchild.children:
                                if greatgrandchild.label == "t:time:MONTH":
                                    record['date']['month'] = greatgrandchild.token
                                elif greatgrandchild.label == "t:time:DATE":
                                    record['date']['date'] = greatgrandchild.token
                                elif greatgrandchild.label == "t:time:YEAR":
                                    record['date']['year'] = greatgrandchild.token
                        if grandchild.label == "emigration_vessel":
                            prev_label_was_VESSEL_HAS_ORIGIN: False
                            for greatgrandchild in grandchild.children:
                                if greatgrandchild.label == "t:emigration:VESSEL":
                                    record['vessel']['name'] = greatgrandchild.token
                                    prev_label_was_VESSEL_HAS_ORIGIN = False
                                if greatgrandchild.label == "t:emigration:VESSEL_HAS_ORIGIN":
                                    prev_label_was_VESSEL_HAS_ORIGIN = True
                                if greatgrandchild.label == "t:location:NAME":
                                    if prev_label_was_VESSEL_HAS_ORIGIN:
                                        record['vessel']['origin'] = greatgrandchild.token
            return [record]




    @staticmethod
    ## this method is NOT reading parse trees with 100% recall (see records[1174])
    def discretize_parents(root_node):
        if root_node.label == "fam:parents":
            collection = []
            for child in root_node.children:
                SequenceParser.find_parent(child, collection)
            ## merg
            both = []
            consolidated = []
            for parent in collection:
                if parent['type'] == "BOTH":
                    for k,v in parent.items():
                        if k != "type":
                            both.append({k: v})
            if len(both) > 0:
                for parent in collection:
                    if parent['type'] != "BOTH":
                        for d in both:
                            parent.update(d)
                        consolidated.append(parent)
                return consolidated
            else:
                return collection

    @staticmethod
    def find_parent(node, collection):
        ## called on a parent_start node
        if node.label is "parent_start":
            record = {}
            for child in node.children:
                if child.label == "parent_type":
                    for grandchild in child.children:
                        if grandchild.label == "t:person:FATHER":
                            record['type'] = "FATHER"
                        elif grandchild.label == "t:person:MOTHER":
                            record['type'] = "MOTHER"
                        elif grandchild.label == "t:person:PARENTS":
                            record['type'] = "BOTH"
                elif child.label == "parent_location":
                    for grandchild in child.children:
                        if grandchild.label == "t:location:NAME":
                            record['located_in'] = grandchild.token
                elif child.label == "parent_status":
                    for grandchild in child.children:
                        if grandchild.label == "t:person:IS_DEAD":
                            record['status'] = "dead"
                        elif grandchild.label == "t:person:IS_ALIVE":
                            record['status'] = "alive"
                elif child.label == "t:person:NAME":
                    record['name'] = child.token
                elif child.label == "parent_start":
                    SequenceParser.find_parent(child, collection)
            collection.append(record)


    @staticmethod
    def create_parse_tree(labeled_record):
        stmt_lists, token_lists, remarks_lists = SequenceParser.split_lists_by_stmt_labels(labeled_record.statement_labels,
                                                                                           labeled_record.token_labels,
                                                                            [item[0] for item in labeled_record.remarks_labels])

        record_root_node = ParseTree.TreeNode(labeled_record.row['Name'])
        for label_idx in range(len(stmt_lists)):
            label_tag = stmt_lists[label_idx][0]
            if label_tag in Rules.Rules.ignored_tags:
                continue
            label_rules = Rules.Rules.get_rules_by_tag(label_tag)
            label_root_node = SequenceParser.get_root_from_parse_tree(token_lists[label_idx], remarks_lists[label_idx], label_tag,
                                                       label_rules)
            record_root_node.children.append(label_root_node)
        return record_root_node

    @staticmethod
    def get_root_from_parse_tree(tokens, remarks, tag_name, rules):
        root = ParseTree.TreeNode(tag_name)
        nodes = list()
        for idx in range(len(tokens)):
            token_tag = tokens[idx]
            token = remarks[idx]
            nodes.append(ParseTree.TreeNode(token_tag, token))
        while True:
            updated_tokens, updated_remarks, updated_nodes = Rules.Rules.parse_tree_by_label(rules, tokens, remarks, nodes)
            if len(updated_tokens) == len(tokens) and updated_tokens == tokens:
                # add the rest of the unattached nodes to root
                for node in nodes:
                    root.children.append(node)
                break
            else:
                tokens = updated_tokens
                nodes = updated_nodes
        return root

    @staticmethod
    def split_lists_by_stmt_labels(stmt_labels, token_labels, remarks_labels):
        if (len(stmt_labels) != len(token_labels) and len(token_labels) != len(remarks_labels)) or len(
                stmt_labels) == 0:
            return None
        output_stmt_labels = []
        output_token_labels = []
        output_remarks_labels = []
        prev_label_idx = 0
        prev_label = stmt_labels[prev_label_idx]
        for idx in range(1, len(stmt_labels)):
            label = stmt_labels[idx]
            if label != prev_label:
                output_stmt_labels.append(stmt_labels[prev_label_idx:idx])
                output_token_labels.append(token_labels[prev_label_idx:idx])
                output_remarks_labels.append(remarks_labels[prev_label_idx:idx])
                prev_label_idx = idx
                prev_label = label
        output_stmt_labels.append(stmt_labels[prev_label_idx:])
        output_token_labels.append(token_labels[prev_label_idx:])
        output_remarks_labels.append(remarks_labels[prev_label_idx:])
        return output_stmt_labels, output_token_labels, output_remarks_labels