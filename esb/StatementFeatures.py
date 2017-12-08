from functools import partial
import re

class StatementFeatures:

    @staticmethod
    def __emit_word_features(rel_pos, word):
        features = {}
        for f in StatementFeatures.__word_feature_functions().items():
            features.update({str(rel_pos) + ":" + f[0]: f[1](word)})
        return features

    @staticmethod
    def get_word_features(sentence,i):
        features = {}
        for x in range(i - 3, i + 4):
            if 0 <= x < len(sentence):
                features.update(StatementFeatures.__emit_word_features(-(i - x), sentence[x][0]))
                if StatementFeatures.__word_within_open_brackets(sentence, x):
                    features.update({'in-brackets': True})
                if StatementFeatures.__word_within_open_parens(sentence, x):
                    features.update({'in-parens': True})
        if i == 0:
            features.update({'BOS' : True})
        if i == len(sentence) - 1:
            features.update({'EOS': True})
        return features

    @staticmethod
    def __word_within_open_brackets(sentence,i):
        opened = False
        for x in range(0,i):
            if sentence[x] == "[":
                opened = True
            elif sentence[x] == "]":
                opened = False
        return opened

    @staticmethod
    def __word_within_open_parens(sentence,i):
        opened = False
        for x in range(0,i):
            if sentence[x] == "(":
                opened = True
            elif sentence[x] == ")":
                opened = False
        return opened

    @staticmethod
    def __word_feature_functions():
        return {
            "word.contains.digit": StatementFeatures.__contains_digit,
            "word.is.delimiter": StatementFeatures.__is_delimiter,
            "word.is.start.token": StatementFeatures.__is_start,
            "word.is.end.token": StatementFeatures.__is_end,
            "word.is.parent.token": StatementFeatures.__is_parent_token,
            "word.is.is": StatementFeatures.__is_is,
            "word.is.relationship.token": StatementFeatures.__is_relationship_token,
            "word.is.wife.husband.token": StatementFeatures.__is_wife_husband,
            "word.is.father.mother.token": StatementFeatures.__is_father_mother,
            "word.is.brother.sister.token": StatementFeatures.__is_brother_sister,
            "word.is.bracket.open": StatementFeatures.__is_bracket_open,
            "word.is.bracket.close": StatementFeatures.__is_bracket_close,
            "word.is.child.token": StatementFeatures.__is_child_token,
            "word.is.ship": StatementFeatures.__is_ship,
            "word.is.year": StatementFeatures.__is_year,
            "word.is.lower": str.islower,
            "word.is.title": str.istitle,
            "word.is.upper": str.isupper,
            "word.prefix.trigram" : partial(StatementFeatures.__prefix, 3),
            "word.prefix.bigram": partial(StatementFeatures.__prefix, 2),
            "word.suffix.trigram": partial(StatementFeatures.__suffix, -3),
            "word.suffix.bigram": partial(StatementFeatures.__suffix, -2),
        }

    @staticmethod
    def get_sentence_features(sentence):
        return [StatementFeatures.get_word_features(sentence, i) for i in range(len(sentence))]

    @staticmethod
    def get_sentence_labels(sentence):
        return [statement_label for token, statement_label, token_label in sentence]

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
        if dc == "par" or dc == "parent":
            return True
        return False

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
        if dc in ["single", "married", "mar"]:
            return True
        return False

    @staticmethod
    def __is_wife_husband(input):
        dc = input.lower()
        if dc in ["wife","husband","wf","husb"]:
            return True
        return False\

    @staticmethod
    def __is_father_mother(input):
        dc = input.lower()
        if dc in ["father","mother","fa","mo"]:
            return True
        return False

    @staticmethod
    def __is_brother_sister(input):
        dc = input.lower()
        if dc in ['bro', 'sis', 'brother', 'sister', 'brothers', 'sisters', 'bro', 'bros', 'sis']:
            return True
        return False

    @staticmethod
    def __is_child_token(input):
        dc = input.lower()
        if dc in ['child', 'children', 'chld','ch', 'son', 'sons', 'daughter', 'daughters']:
            return True
        return False

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
        for j in range(1,div + 1):
            if pos <= j*(sent_length / float(div)):
                return j

    @staticmethod
    def __is_widow_token(input):
        dc = input.lower()
        if dc == "wid" or dc == "widow":
            return True
        return False

    @staticmethod
    def __is_year(input):
        dc = input.lower()
        try:
            num = int(dc)
            return (1600 < num < 1980)
        except:
            return False

    # @staticmethod
    # def __is_preposition(input):
    #     dc = input.lower()


