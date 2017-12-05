# Emigrant Savings Bank

Sample use:
```python
import esb

## Load in all of the 25k records
records = esb.Utils.Utils.auto_load()

## See the (unlabeled) original remarks field of a record
records[0].remarks()

## Train a CRF classifier
classifier = esb.Classifier.Classifier()
classifier.load_training("./data/labels-training/esb_training_64.csv")
classifier.train()

## Label a single record, and visualize the results
classifier.label(records[0])
records[0].print()

## Gather a list of all predicted labels
records[0].token_labels

## Label first 1k records (will take a few moments)
labeled_subset = list(map( lambda x: classifier.label(x), records[0:1000]))
```
