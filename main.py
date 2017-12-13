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
    # labeled_subset = list(map(lambda x: tc.label(sc.label(x)), records[0:1000]))
    labeled_subset = list(map(lambda x: tc.label(sc.label(x)), records[0:50]))

    subset_with_tag = get_specific_tag_records(labeled_subset, Tags.Thematic.FAM_SIBLINGS)

    # handling for a specific label
    first_rule, siblings_rules = Rules.get_siblings_rules()

    for idx in range(len(subset_with_tag)):
        record = subset_with_tag[idx]
        root = get_root_from_parse_tree(record, Tags.Thematic.FAM_SIBLINGS, siblings_rules)
        print('-------------------------')
        TreeNode.preorder_print(root)

    print("PAUSE")

# return the root of parsed tree for a specific tag
def get_root_from_parse_tree(record, tag_name, rules):

    root = TreeNode(tag_name)

    labels = [str(idx[0]) for idx in record]
    labels_length = len(labels)

    nodes = list()

    for label, token in record:
        nodes.append(TreeNode(label, token))

    while True:
        labels, nodes = Rules.brute_force(rules, labels, nodes)

        if labels_length == len(labels):
            # add the rest of the unattached nodes to root
            for node in nodes:
                root.children.append(node)
            break
        else:
            labels_length = len(labels)

    return root


# Gather a specific type of Tag into a list
def get_specific_tag_records(records, tag_name):

    output = list()

    for record_idx in range(len(records)):
        record = records[record_idx]

        same_tag_tokens = []
        for token_idx in range(len(record.statement_labels)):
            token = record.statement_labels[token_idx]

            if tag_name == token:
                tup = (record.token_labels[token_idx], record.remarks_labels[token_idx][0])
                same_tag_tokens.append(tup)

        if len(same_tag_tokens) > 0:
            output.append(same_tag_tokens)

    return output

if __name__ == '__main__':
    main()
