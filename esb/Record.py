from esb import Utils

class Record:
    def __init__(self, row):
        self.row = row
        self.token_labels = None
        self.is_parsed = False
        self.token_v2_labels = None

    def remarks(self):
        return self.row['Remarks']

    def remarks_tokens(self, encapsulate=True):
        if encapsulate:
            return Utils.Utils.label_tokenize(self.remarks())
        else:
            return Utils.Utils.tokenize(self.remarks(), True)

    def print(self):
        if self.token_labels is not None:
            for x in range(0,len(self.token_labels)):
                if (self.token_v2_labels != None):
                    print(self.token_labels[x], "\t", self.remarks_tokens()[x][0], "\t", self.token_v2_labels[x])
                else:
                    print(self.token_labels[x],"\t",self.remarks_tokens()[x][0])
