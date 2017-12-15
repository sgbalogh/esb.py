from esb import ParseTree
from esb import Rules
from esb.Triple import Triple

class SequenceParser:

    @staticmethod
    def discretize_tree(parse_tree):
        triples = []
        subject_profile = {}
        print(parse_tree.children)
        for theme in parse_tree.children:
            if theme.label is "fam:siblings":
                triples.append(SequenceParser.__read_siblings(theme, subject_profile))

    # @staticmethod
    # def dfs(root):
    #     entities = []
    #     for child in root.children:
    #         if child.dfs_color is "white":
    #             dfs.

    # @staticmethod
    # def dfs_visit(node, predicates):

    # @staticmethod
    # def __read_siblings(sibling_root, subject_profile):
    #     siblings = []
    #     churn = True
    #     while (churn):


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