import csv
from esb import Record


class Utils:
    @staticmethod
    def label_tokenize(input):
        return list(map(lambda x: (x, None), Utils.tokenize(input, True)))

    @staticmethod
    def tokenize(input, append_start_end=False):
        delimiters_omit = [' ', '\n', '\r']
        tokens = ['START'] if append_start_end else []
        buffer = ''
        for elem in input:
            if elem in delimiters_omit:
                if len(buffer) > 0:
                    tokens.append(buffer)
                    buffer = ''
            elif not elem.isalnum():
                if len(buffer) > 0:
                    tokens.append(buffer)
                    buffer = ''
                tokens.append(elem)
            else:
                buffer += elem
        if len(buffer) > 0:
            tokens.append(buffer)
        if append_start_end:
            tokens.append('END')
        return tokens

    @staticmethod
    def load_rows(path_to_csv):
        rows = []
        headers = []
        with open(path_to_csv, 'r', encoding="utf-8") as csvfile:
            rdr = csv.reader(csvfile)
            index = -1
            for row in rdr:
                index += 1
                if index == 0:
                    headers = row
                else:
                    rows.append(dict(zip(headers, row)))
        return rows

    @staticmethod
    def load_records(rows):
        return list(map(lambda x: Record.Record(x), rows))

    @staticmethod
    def auto_load():
        return Utils.load_records(Utils.load_rows("./data/esb25k.csv"))
