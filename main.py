import esb
from esb.Tags import Tags
from esb.Rules import Rules
from esb.ParseTree import *
from esb.Stack import Stack



def main():
    ## Load in all of the 25k records
    records = esb.Utils.Utils.auto_load()

    ## See the (unlabeled) original remarks field of a record
    records[0].remarks()

    ## The package contains two types of CRF models; one which is used to predict the general theme of a statement,
    ## another which is used to label individual tokens. These are intended to be used one after another, and the
    ## predicted statement/theme labels are fed into the individual token model.

    ## Train a CRF statement/theme classifier
    sc = esb.StatementClassifier.StatementClassifier()
    sc.load_training("./data/labels-training/esb_training_full.csv")
    sc.train()

    ## Train a CRF individual-token classifier
    tc = esb.TokenClassifier.TokenClassifier()
    tc.load_training("./data/labels-training/esb_training_full.csv")
    tc.train()

    ## Fully label a record entry, and print the result
    # tc.label(sc.label(records[0])).print()

    ## Label first 1k records (will take a few moments)
    labeled_subset = list(map(lambda x: tc.label(sc.label(x)), records[0:50]))

    for idx in range(len(labeled_subset)):
        record = labeled_subset[idx]
        stmt_lists, token_lists, remarks_lists = split_lists_by_stmt_labels(record.statement_labels,
                                                                            record.token_labels,
                                                                            [item[0] for item in record.remarks_labels])

        record_root_node = TreeNode(record.row['Name']) #use account owner's name as root node

        for label_idx in range(len(stmt_lists)):
            label_tag = stmt_lists[label_idx][0]

            if label_tag in Rules.ignored_tags:
                continue

            label_rules = Rules.get_rules_by_tag(label_tag)

            label_root_node = get_root_from_parse_tree(token_lists[label_idx], remarks_lists[label_idx], label_tag,
                                                       label_rules)

            record_root_node.children.append(label_root_node)

        # TreeNode.preorder_print(record_root_node)
        print("yo")

#TODO: siblings tag - add owner's last name into them
#TODO: use hashmap to store entity nodes [name, node]
#TODO: attach Unknown tag with previous tag as attribute/properity to node

# return the root of parsed tree for a specific tag
def get_root_from_parse_tree(tokens, remarks, tag_name, rules):

    root = TreeNode(tag_name)
    nodes = list()

    for idx in range(len(tokens)):
        token_tag = tokens[idx]
        token = remarks[idx]
        nodes.append(TreeNode(token_tag, token))

    while True:
        updated_tokens, updated_remarks, updated_nodes = Rules.parse_tree_by_label(rules, tokens, remarks, nodes)

        if len(updated_tokens) == len(tokens) and updated_tokens == tokens:
            # add the rest of the unattached nodes to root
            for node in nodes:
                root.children.append(node)
            break
        else:
            tokens = updated_tokens
            nodes = updated_nodes

    return root


# Gather a specific type of Tag into a list
# def get_specific_tag_records(records, tag_name):
#
#     output = list()
#
#     for record_idx in range(len(records)):
#         record = records[record_idx]
#
#         same_tag_tokens = []
#         for token_idx in range(len(record.statement_labels)):
#             token = record.statement_labels[token_idx]
#
#             if tag_name == token:
#                 tup = (record.token_labels[token_idx], record.remarks_labels[token_idx][0])
#                 same_tag_tokens.append(tup)
#
#         if len(same_tag_tokens) > 0:
#             output.append(same_tag_tokens)
#
#     return output


def split_lists_by_stmt_labels(stmt_labels, token_labels, remarks_labels):
    if (len(stmt_labels) != len(token_labels) and len(token_labels) != len(remarks_labels)) or len(stmt_labels) == 0:
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

if __name__ == '__main__':
    main()
