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
        i_statement_label = sentence[i][1]
        for x in range(i - 3, i + 4):
            if 0 <= x < len(sentence):
                rel_pos_str = str(-(i - x))
                features.update(TokenFeatures.__emit_word_features(-(i - x), sentence[x][0], sentence[x][1]))
                features.update({ rel_pos_str + ':same-statement-label': i_statement_label == sentence[x][1]})
                if Features.word_within_open_brackets(sentence, x):
                    features.update({rel_pos_str + ':in-brackets': True})
                if Features.word_within_open_parens(sentence, x):
                    features.update({rel_pos_str + ':in-parens': True})
        if i == 0:
            features.update({'BOS' : True})
        if i == len(sentence) - 1:
            features.update({'EOS': True})
        return features

    @staticmethod
    def get_sentence_features(sentence):
        return [TokenFeatures.get_word_features(sentence, i) for i in range(len(sentence))]

    @staticmethod
    def get_sentence_labels(sentence):
        return [token_label for token, statement_label, token_label in sentence]

    @staticmethod
    def get_sentence_tokens(sentence):
        return [token for token, statement_label, token_label in sentence]