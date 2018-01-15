from esb import Utils


class Record:
    def __init__(self, row):
        self.row = row
        self.statement_labels = None
        self.token_labels = None
        self.remarks_labels = None

    def remarks(self):
        return self.row['Remarks']

    def account_number(self):
        return self.row['Account']

    def remarks_tokens(self, encapsulate=True):
        if self.remarks_labels is None:
            self.remarks_labels = Utils.Utils.label_tokenize(self.remarks())
        if encapsulate:
            return self.remarks_labels
        else:
            return [remark[0] for remark in self.remarks_labels]

    def print_only_statement(self):
        for x in range(0, len(self.token_labels)):
            print(self.statement_labels[x], "\t", self.remarks_tokens()[x][0])

    def print_statement_and_token(self):
        for x in range(0, len(self.token_labels)):
            print(
                str(x),
                self.statement_labels[x],
                "\t",
                self.remarks_tokens()[x][0],
                "\t",
                self.token_labels[x])

    def print(self):
        if self.statement_labels is not None and self.token_labels is not None:
            self.print_statement_and_token()
        elif self.statement_labels is not None:
            self.print_only_statement()
