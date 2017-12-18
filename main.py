import esb
from esb.Tags import Tags
from esb.Rules import Rules
from esb.ParseTree import *
from esb.SequenceParser import SequenceParser


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
    labeled_subset = list(map(lambda x: tc.label(sc.label(x)), records[:500]))

    entity_subset = []

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

            if label_tag == Tags.Thematic.FAM_CHILDREN:
                print("PAUSE")

            record_root_node.children.append(label_root_node)

        record_entity = {}
        for subtree in record_root_node.children:
            if subtree.label == Tags.Thematic.FAM_SIBLINGS:
                record_entity['siblings'] = SequenceParser.parse_siblings_subtree(subtree)

            elif subtree.label == Tags.Thematic.FAM_PARENTS:
                record_entity['parents'] = SequenceParser.parse_parents_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_EMIGRATION:
                record_entity['emigration'] = SequenceParser.parse_emigration_subtree(subtree)

            elif subtree.label == Tags.Thematic.FAM_CHILDREN:
                record_entity['children'] = SequenceParser.parse_children_subtree(subtree)

            elif subtree.label == Tags.Thematic.FAM_SPOUSE:
                record_entity['spouse'] = SequenceParser.parse_spouse_subtree(subtree)

            elif subtree.label == Tags.Thematic.META_RECORD:
                record_entity['record_reference'] = SequenceParser.parse_record_reference_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_AGE:
                record_entity['age'] = SequenceParser.parse_age_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_BIO:
                record_entity['bio'] = SequenceParser.parse_bio_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_MARTIAL:
                record_entity['martial'] = SequenceParser.parse_martial_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_NATIVEOF:
                record_entity['native_of'] = SequenceParser.parse_native_of_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_OCCUPATION:
                record_entity['occupation'] = SequenceParser.parse_occupation_subtree(subtree)

            elif subtree.label == Tags.Thematic.SUBJ_RESIDENCE:
                record_entity['residence'] = SequenceParser.parse_residence_subtree(subtree)

        if len(record_entity) > 0:
            entity_subset.append(record_entity)

    print("yo")


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
                if node.label not in Rules.ignored_tags:
                    root.children.append(node)
            break
        else:
            tokens = updated_tokens
            nodes = updated_nodes

    return root


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
