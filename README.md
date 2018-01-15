# esb.py

A Python-based set of tools, models, and training data for extracting structured claims from natural language found in historical account data from New York City's [Emigrant Savings Bank](https://en.wikipedia.org/wiki/Emigrant_Savings_Bank). Allows users to turn the corpus into a queryable graph network.

This code-base was submitted as a project for the graduate course [Statistical Natural Language Processing](https://cs.nyu.edu/courses/fall17/CSCI-GA.3033-008/) at New York University's Courant Institute. The authors' report submitted for the course can be found in [docs/report.pdf](docs/report.pdf).

### Overview

The dataset consists of account entries, each possessing a natural language "remarks" field, such as:

> She Nat of Ferrymount, 6 miles from Mt Mellick, Queens, Ire - Arr Jul 1844 per Fairfield from LP - Fa in Ire John Henry, Mo dead Bridget Fahy, 4 Bros Pat’k, John & James in US, Martin in Ire, 3 Sis Ellen, Honora & ___ see 3989

This library provides tools for:
1. Assigning theme labels to subsets of a remark text
2. Assigning token-level symbols to a remark text
3. Extracting a machine-readable synthesis of named entities and named relations, with the goal of building a graph network

Two conditional random field (CRF) models are training on labeled data to achieve the first two goals.

Extracting a machine-readable synthesis from CRF-predicted label sequences is done using formal context-free grammar parsing, and by subsequently interpreting the resulting parse-tree.

Example output from the remarks field shown above is below (in JSON):
```json
{
  "native_of": {
    "location": "Ferrymount",
    "distance_from": {
      "from": "Mt Mellick , Queens , Ire",
      "distance": "6 miles"
    }
  },
  "emigration": [
    {
      "date": {
        "month": "Jul",
        "year": "1844"
      },
      "vessel": {
        "vessel": "Fairfield",
        "location": "LP"
      }
    }
  ],
  "parents": [
    {
      "type": "Father",
      "location": "Ire",
      "name": "John Henry"
    },
    {
      "type": "Mother",
      "status": "Dead",
      "name": "Bridget Fahy"
    }
  ],
  "siblings": [
    {
      "type": "BROTHERS",
      "name": "Pat ' k"
    },
    {
      "type": "BROTHERS",
      "name": "John"
    },
    {
      "type": "BROTHERS",
      "name": "James",
      "location": "US"
    },
    {
      "type": "BROTHERS",
      "name": "Martin",
      "location": "Ire"
    },
    {
      "type": "SISTERS",
      "name": "Ellen"
    },
    {
      "type": "SISTERS",
      "name": "Honora"
    }
  ],
  "record_reference": [
    [
      {
        "see": "see",
        "account": "3989"
      }
    ]
  ]
}
```
### Data

- Data for 25k accounts are captured in `data/esb25k.csv`
- Labeled training data for the conditional random field models is in `data/labels-training/esb_training_full.csv`
  - More detail on the construction of the training set can be found in the project report document, `docs/report.pdf`

### Metrics

Metrics were calculated at the level of CRF-predictions, and also at the final "extracted record" (end-to-end) level.

#### CRF Models

On 30 randomly sampled and human evaluated records, the accuracy of our two CRF models is:

| CRF Model | Evaluated Records | Correct Labels | Incorrect Labels | Accuracy|
| ------------- |:-------------:| :-------------:| :-------------:| :-------------:|
| Statement / theme    | 30 | 1245| 0| **1.0** |
| Token / POS      | 30    | 1207 | 38 | **0.9694**


#### End-to-end

On 25 randomly sampled and human evaluated records, our precision and recall for extractable claims is:

| Metric        | Context-free Grammar Interpreter|
| ------------- |:-------------:|
| Precision    | 0.9612 |
| Recall      | 0.7647 |
| F-measure | 0.8517 |

More can be read about our testing design in the project report.

### Setup

Install requirements:
```bash
$ make
```

Verify that the library is configured properly:
```bash
$ make test
```

### Use as library

Sample use:
```python
import esb
import json

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
tc.label(sc.label(records[0])).print()

## Create a parse tree and store the root
pt = esb.SequenceParser.SequenceParser.create_parse_tree(records[0])

## Fully process a record
extracted_record = esb.SequenceParser.SequenceParser.process_completely(records[13000],tc,sc)

## Print the JSON version
print(json.dumps(extracted_record))

## Create a geocoding location normalizer
## (only if you have configured an instance of Mapzen's Pelias)
# normalizer = esb.LocationNormalizer.LocationNormalizer()
# print(normalizer.best_guess("nyc"))

## Label first 1k records (will take a few moments)
labeled_subset = list(map( lambda x: tc.label(sc.label(x)), records[0:1000]))
```
