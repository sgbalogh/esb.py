## This class contains common feature-extraction functions used by both
## CRF models

from functools import partial
from esb.Dictionaries import Dictionaries

class Features:
    @staticmethod
    def word_feature_functions():
        return {
            "word.contains.digit": Features.__contains_digit,
            "word.is.delimiter": Features.__is_delimiter,
            "word.is.start.token": Features.__is_start,
            "word.is.end.token": Features.__is_end,
            "word.is.parent.token": Features.__is_parent_token,
            "word.is.is": Features.__is_is,
            "word.is.relationship.token": Features.__is_relationship_token,
            "word.is.wife.husband.token": Features.__is_wife_husband,
            "word.is.father.mother.token": Features.__is_father_mother,
            "word.is.brother.sister.token": Features.__is_brother_sister,
            "word.is.bracket.open": Features.__is_bracket_open,
            "word.is.bracket.close": Features.__is_bracket_close,
            "word.is.child.token": Features.__is_child_token,
            "word.is.ship": Features.__is_ship,
            "word.is.year": Features.__is_year,
            "word.is.month": Features.__is_month,
            "word.is.common.location.name": Features.__is_common_location_name,
            "word.is.lower": str.islower,
            "word.is.title": str.istitle,
            "word.is.upper": str.isupper,
            "word.prefix.trigram": partial(Features.__prefix, 3),
            "word.prefix.bigram": partial(Features.__prefix, 2),
            "word.suffix.trigram": partial(Features.__suffix, -3),
            "word.suffix.bigram": partial(Features.__suffix, -2),
        }

    @staticmethod
    def get_sentence_features(sentence):
        return [Features.get_word_features(sentence, i) for i in range(len(sentence))]

    @staticmethod
    def get_sentence_labels(sentence):
        return [token_label for token, statement_label, token_label in sentence]

    @staticmethod
    def get_sentence_tokens(sentence):
        return [token for token, statement_label, token_label in sentence]

    @staticmethod
    def __contains_digit(input):
        for c in input:
            if c.isdigit():
                return True
        return False

    @staticmethod
    def __suffix(amount, word):
        return word[amount:]

    @staticmethod
    def __prefix(amount, word):
        return word[0:amount]

    @staticmethod
    def __is_start(input):
        if input == "START":
            return True
        return False

    @staticmethod
    def __is_end(input):
        if input == "END":
            return True
        return False

    @staticmethod
    def __is_delimiter(input):
        for c in input:
            if c == '-' or c == ',':
                return True
        return False

    @staticmethod
    def __is_parent_token(input):
        dc = input.lower()
        return dc in Dictionaries.parent_tokens()

    @staticmethod
    def __is_is(input):
        dc = input.lower()
        if dc == "is":
            return True
        return False

    @staticmethod
    def __is_bracket_open(input):
        if input == "[":
            return True
        return False

    @staticmethod
    def __is_bracket_close(input):
        if input == "]":
            return True
        return False

    @staticmethod
    def __is_relationship_token(input):
        dc = input.lower()
        return dc in Dictionaries.relationship_tokens()

    @staticmethod
    def __is_wife_husband(input):
        dc = input.lower()
        return dc in Dictionaries.spouse_tokens()

    @staticmethod
    def __is_father_mother(input):
        dc = input.lower()
        return dc in Dictionaries.mother_father_tokens()

    @staticmethod
    def __is_brother_sister(input):
        dc = input.lower()
        return dc in Dictionaries.brother_sister()

    @staticmethod
    def __is_child_token(input):
        dc = input.lower()
        return dc in Dictionaries.children()

    @staticmethod
    def __is_ship(input):
        dc = input.lower()
        if dc == "ship":
            return True
        return False

    @staticmethod
    def __segment_of_sentence(sent, i, div):
        sent_length = len(sent)
        pos = i + 1
        for j in range(1, div + 1):
            if pos <= j * (sent_length / float(div)):
                return j

    @staticmethod
    def __is_widow_token(input):
        dc = input.lower()
        return dc in Dictionaries.widow_tokens()

    @staticmethod
    def __is_year(input):
        dc = input.lower()
        try:
            num = int(dc)
            return ((1600 < num < 1980) or (0 <= num <= 99))
        except:
            return False

    @staticmethod
    def __is_month(input):
        dc = input.lower()
        return dc in Dictionaries.months()

    @staticmethod
    def __is_common_location_name(input):
        dc = input.lower()
        return dc in Dictionaries.common_locations()