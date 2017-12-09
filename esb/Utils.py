import csv
import sys

from esb import Record

csv.field_size_limit(sys.maxsize)

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
        with open(path_to_csv, 'r') as csvfile:
            rdr = csv.reader(csvfile)
            index = -1
            for row in rdr:
                index += 1
                if index == 0:
                    headers = row
                else:
                    rows.append(dict(zip(headers,row)))
        return rows

    @staticmethod
    def load_records(rows):
        return list(map(lambda x: Record.Record(x), rows))

    @staticmethod
    ## Geonames util
    def load_geonames_rows(path_to_txt):
        rows = []
        headers = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class",
                   "feature code", "country code", "cc2", "admin1 code", "admin2 code", "admin3 code", "admin4 code",
                   "population", "elevation", "dem", "timezone", "modification date"]
        with open(path_to_txt, 'r', encoding='utf-8') as csvfile:
            rdr = csv.reader(csvfile, delimiter=',')
            for row in rdr:
                if len(row) != 19:
                    "Incorrect number of columns detected..."
                rows.append(dict(zip(headers, row)))
        return rows


    @staticmethod
    ## Auto load records from ESB
    def auto_load():
        return Utils.load_records(Utils.load_rows("./data/esb25k.csv"))
