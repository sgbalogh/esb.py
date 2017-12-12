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

    siblings_subset = list()

    for record_idx in range(len(labeled_subset)):
        record = labeled_subset[record_idx]

        # has siblings token
        siblings_tokens = []
        for token_idx in range(len(record.statement_labels)):
            token = record.statement_labels[token_idx]

            if Tags.Thematic.FAM_SIBLINGS == token:
                tup = (record.token_labels[token_idx], record.remarks_labels[token_idx][0])
                siblings_tokens.append(tup)

        if len(siblings_tokens) > 0:
            siblings_subset.append(siblings_tokens)


    # shift-reduce algorithm
    stack = Stack()
    first_rule, siblings_rules = Rules.get_siblings_rules()

    for idx in range(len(siblings_subset)):
        record = siblings_subset[idx]
        root = TreeNode(Tags.Thematic.FAM_SIBLINGS)

        for label, token in record:
            stack.push(label)
            print(label, token)

            #TODO: if next token is a terminal or zero_or_more, push it out as well
            stack = Rules.shift_reduce(siblings_rules, first_rule, stack)

            # matched_rules = Rules.get_matched_rules(siblings_rules, stack)

            # if more than one matched rule, take the longest one
            # if len(matched_rules) > 0:
            #     rule = max(matched_rules, key=len)
            #
                # update stack with rule





    print("PAUSE")

if __name__ == '__main__':
    main()
