import csv
import fileinput
import json
import sys
from esb.TokenFeatures import TokenFeatures
from esb.Record import Record
from esb.Tags import Tags
import sklearn_crfsuite
from sklearn_crfsuite import metrics


class TokenClassifier:
    def __init__(self, training_data=None):
        self.training_set_labeled = []
        self.training_set_features = []
        self.training_set_labels = []
        self.validation_set_labeled = []
        self.validation_set_features = []
        self.validation_set_labels = []
        self.crf = None

    def load_labeled_data(self, path_to_csv):
        rows = []
        headers = []
        labeled_data = []
        with open(path_to_csv, 'r', encoding='utf-8') as csvfile:
            rdr = csv.reader(csvfile)
            index = -1
            for row in rdr:
                index += 1
                if index == 0:
                    headers = row
                elif index > 1:
                    rows.append(dict(zip(headers, row)))
        example_number = -1
        example = None
        for row in rows:
            sentence_number = int(row['training-example'])
            if sentence_number > example_number:
                example_number = sentence_number
                if example is None:
                    example = []
                else:
                    labeled_data.append(example)
                    example = []
            example.append(
                (row['token'],
                 row['label:thematic'],
                    row['label:token']))
        labeled_data.append(example)
        return labeled_data

    def listen(self):
        for line in fileinput.input(sys.argv[3:]):
            entry = Record(line.rstrip())
            print(json.dumps(self.label(entry).categories))

    def load_training(self, path_to_csv):
        self.training_set_labeled = self.load_labeled_data(path_to_csv)
        self.__process_training_data()

    def load_validation(self, path_to_csv):
        self.validation_set_labeled = self.load_labeled_data(path_to_csv)
        self.__process_validation_data()

    def __process_training_data(self):
        self.training_set_features = [
            TokenFeatures.get_sentence_features(s) for s in self.training_set_labeled]
        self.training_set_labels = [
            TokenFeatures.get_sentence_labels(s) for s in self.training_set_labeled]

    def __process_validation_data(self):
        self.validation_set_features = [
            TokenFeatures.get_sentence_features(s) for s in self.validation_set_labeled]
        self.validation_set_labels = [
            TokenFeatures.get_sentence_labels(s) for s in self.validation_set_labeled]

    def train(self):
        self.crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=0.1,
            c2=0.1,
            max_iterations=1000,
            all_possible_transitions=True,
            verbose=True
        )
        self.crf.fit(self.training_set_features, self.training_set_labels)

    def validation_metrics(self):
        labels = list(self.crf.classes_)
        validation_predictions = self.crf.predict(self.validation_set_features)
        return metrics.flat_f1_score(
            self.validation_set_labels,
            validation_predictions,
            average='weighted',
            labels=labels)

    def print_validation_metrics_per_class(self):
        validation_predictions = self.crf.predict(self.validation_set_features)
        sorted_labels = sorted(
            list(self.crf.classes_),
            key=lambda name: (name[1:], name[0])
        )
        print(
            metrics.flat_classification_report(
                self.validation_set_labels,
                validation_predictions,
                labels=sorted_labels,
                digits=5))

    def predict_labeled_tokens(self, labeled_tokens):
        features_set = [TokenFeatures.get_sentence_features(labeled_tokens)]
        return self.crf.predict(features_set)[0]

    def label(self, record):
        labeled_record = None

        if isinstance(record, list):
            labeled_record = list(self.label(x) for x in record)
        else:
            if record.statement_labels is not None:
                record.token_labels = self.predict_labeled_tokens(
                    list(zip(map(lambda x: x[0], record.remarks_tokens()), record.statement_labels)))
                labeled_record = record
        if labeled_record is not None:
            # list of token tags to concatenate
            concat_token_tags = [
                Tags.Token.LOCATION_NAME,
                Tags.Token.WORK_EMPLOYER_NAME,
                Tags.Token.PERSON_NAME,
                Tags.Token.REL_IS_NATIVE_OF,
                Tags.Token.META_PARENTHETICAL,
                Tags.Token.EMIGRATION_VESSEL,
                Tags.Token.TIME_MONTH,
                Tags.Token.EMIGRATION_VIA,
                Tags.Token.REL_HAS_SPOUSE,
                Tags.Token.UNKNOWN,
                Tags.Token.REL_IS_WIDOW_OF,
                Tags.Token.REL_HAS_HUSBAND,
                Tags.Token.REL_HAS_WIFE,
                Tags.Token.PERSON_IS_WIDOWED,
                Tags.Token.META_NO_REMARKS,
                Tags.Token.META_IS_SAME_AS,
                Tags.Token.PERSON_AGE,
                Tags.Token.PERSON_IS_SINGLE,
                Tags.Token.WORK_OCCUPATION,
                Tags.Token.WORK_WORKS_FOR,
                Tags.Token.RESIDENTIAL_LIVED_WITH,
                Tags.Token.RESIDENTIAL_LIVES_WITH,
                Tags.Token.RESIDENTIAL_FORMERLY_LOCATED_AT,
                Tags.Token.RESIDENTIAL_CURRENTLY_LIVING_AT,
                Tags.Token.META_ACCOUNT_CLOSED,
                Tags.Token.DELIMITER]

            return self.concatenate_tokens_by_tags(
                labeled_record, concat_token_tags)
        else:
            return False

    @staticmethod
    def concatenate_tokens_by_tags(record, tags):

        size = len(record.remarks_tokens())

        output_record = record

        new_remarks_tokens = list()
        new_statement_labels = list()
        new_token_labels = list()

        current_remark = None
        current_token_tag = None

        for idx in range(len(record.remarks_tokens())):
            label = record.token_labels[idx]
            token = record.remarks_tokens()[idx]

            if label in tags:
                if current_remark is None:
                    # first remark label with name
                    current_remark = list(token)
                    current_token_tag = label
                else:
                    # append to previous label
                    current_remark[0] = current_remark[0] + ' ' + token[0]

                if idx + \
                        1 < size and current_token_tag != record.token_labels[idx + 1] or idx + 1 == size:
                    new_remarks_tokens.append(tuple(current_remark))
                    new_statement_labels.append(record.statement_labels[idx])
                    new_token_labels.append(record.token_labels[idx])
                    current_token_tag = None
                    current_remark = None

            else:
                new_remarks_tokens.append(token)
                new_statement_labels.append(record.statement_labels[idx])
                new_token_labels.append(record.token_labels[idx])

        output_record.statement_labels = new_statement_labels
        output_record.token_labels = new_token_labels
        output_record.remarks_labels = new_remarks_tokens

        return output_record
