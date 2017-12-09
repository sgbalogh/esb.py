from esb.Features import Features

class TokenFeatures:

    @staticmethod
    def __emit_word_features(rel_pos, word, statement_label):
        features = {}
        features.update( {str(rel_pos) + ":" + statement_label: True }) ## This captures the prev. predicted statement label
        for f in Features.word_feature_functions().items():
            features.update({str(rel_pos) + ":" + f[0]: f[1](word)})
        return features

    @staticmethod
    def get_word_features(sentence,i):
        features = {}
        for x in range(i - 3, i + 4):
            if 0 <= x < len(sentence):
                features.update(TokenFeatures.__emit_word_features(-(i - x), sentence[x][0], sentence[x][1]))
                if TokenFeatures.__word_within_open_brackets(sentence, x):
                    features.update({'in-brackets': True})
                if TokenFeatures.__word_within_open_parens(sentence, x):
                    features.update({'in-parens': True})
        if i == 0:
            features.update({'BOS' : True})
        if i == len(sentence) - 1:
            features.update({'EOS': True})
        return features

    @staticmethod
    def __word_within_open_brackets(sentence, i):
        opened = False
        for x in range(0, i):
            if sentence[x] == "[":
                opened = True
            elif sentence[x] == "]":
                opened = False
        return opened

    @staticmethod
    def __word_within_open_parens(sentence, i):
        opened = False
        for x in range(0, i):
            if sentence[x] == "(":
                opened = True
            elif sentence[x] == ")":
                opened = False
        return opened

    @staticmethod
    def get_sentence_features(sentence):
        return [TokenFeatures.get_word_features(sentence, i) for i in range(len(sentence))]

    @staticmethod
    def get_sentence_labels(sentence):
        return [token_label for token, statement_label, token_label in sentence]

    @staticmethod
    def get_sentence_tokens(sentence):
        return [token for token, statement_label, token_label in sentence]