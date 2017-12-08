# Emigrant Savings Bank

Sample use:
```python
import esb

## Load in all of the 25k records
records = esb.Utils.Utils.auto_load()

## See the (unlabeled) original remarks field of a record
records[0].remarks()

## The package contains two types of CRF models; one which is used to predict the general theme of a statement,
## another which is used to label individual tokens. These are intended to be used one after another, and the
## predicted statement/theme labels are fed into the individual token model.

## Train a CRF statemen/theme classifier
sc = esb.StatementClassifier.StatementClassifier()
sc.load_training("./data/labels-training/esb_training_64.csv")
sc.train()

## Train a CRF individual-token classifier
tc = esb.TokenClassifier.TokenClassifier()
tc.load_training("./data/labels-training/esb_training_64_token_27.csv")
tc.train()

## Fully label a record entry, and print the result
tc.label(sc.label(records[0])).print()

## Label first 1k records (will take a few moments)
labeled_subset = list(map( lambda x: tc.label(sc.label(x)), records[0:1000]))
```
