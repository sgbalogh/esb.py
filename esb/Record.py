from esb import Utils

class Record:
    def __init__(self, row):
        self.row = row
        self.statement_labels = None
        self.token_labels = None
        self.has_labeled_statements = False
        self.has_labeled_tokens = False

    def remarks(self):
        return self.row['Remarks']

    def remarks_tokens(self, encapsulate=True):
        if encapsulate:
            return Utils.Utils.label_tokenize(self.remarks())
        else:
            return Utils.Utils.tokenize(self.remarks(), True)

    def print_only_statement(self):
        for x in range(0, len(self.token_labels)):
            print(self.statement_labels[x], "\t", self.remarks_tokens()[x][0])

    def print_statement_and_token(self):
        for x in range(0, len(self.token_labels)):
            print(self.statement_labels[x], "\t", self.remarks_tokens()[x][0], "\t", self.token_labels[x])

    def print(self):
        if (self.has_labeled_statements and self.has_labeled_tokens):
            self.print_statement_and_token()
        elif (self.has_labeled_statements):
            self.print_only_statement()
