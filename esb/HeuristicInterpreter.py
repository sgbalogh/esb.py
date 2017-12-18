class HeuristicInterpreter:

    @staticmethod
    def interpret(labeled_record):
        tuple_list = list(zip(labeled_record.remarks_tokens(False), labeled_record.statement_labels, labeled_record.token_labels ))
        interpreted_record = {
            "parent_names" : HeuristicInterpreter.find_parent_names(tuple_list),
            "sibling_names": HeuristicInterpreter.find_sibling_names(tuple_list),
            "emigration_account": HeuristicInterpreter.find_emigration_account(tuple_list),
            "native-location": HeuristicInterpreter.find_nativity(tuple_list),
            "linked-accounts": HeuristicInterpreter.find_account_references(tuple_list),
            "father-location": HeuristicInterpreter.find_father_location(tuple_list),
            "mother-location": HeuristicInterpreter.find_mother_location(tuple_list),
            "parents-location": HeuristicInterpreter.find_parents_location(tuple_list),
            "children-number": HeuristicInterpreter.find_number_children(tuple_list)
        }
        return interpreted_record

    @staticmethod
    def __search_for_num_brothers(sequence):
        return None

    @staticmethod
    def find_sibling_names(sequence):
        names = []
        for token,statement,tag in sequence:
            if statement == "fam:siblings":
                if tag == "t:person:NAME":
                    names.append(token)
        return names

    @staticmethod
    def find_parent_names(sequence):
        names = []
        for token, statement, tag in sequence:
            if statement == "fam:parents":
                if tag == "t:person:NAME":
                    names.append(token)
        return names

    @staticmethod
    def find_nativity(sequence):
        names = []
        for token, statement, tag in sequence:
            if statement == "subj:native-of":
                if tag == "t:location:NAME":
                    names.append(token)
        return names

    def find_emigration_account(sequence):
        account = {}
        prior_V_H_O = False
        for token, statement, tag in sequence:
            if statement == "subj:emigration-event":
                if tag == "t:time:MONTH":
                    account['month'] = token
                    prior_V_H_O = False
                elif tag == "t:time:YEAR":
                    account['year'] = token
                    prior_V_H_O = False
                elif tag == "t:emigration:VESSEL_HAS_ORIGIN":
                    prior_V_H_O = True
                elif tag == "t:location:NAME" and prior_V_H_O:
                    account['vessel-origin'] = token
                    prior_V_H_O = False
                elif tag == "t:emigration:VESSEL":
                    account['vessel'] = token
                    prior_V_H_O = False

    def find_number_children(sequence):
        for token, statement, tag in sequence:
            if statement == "fam:children":
                if tag == "t:person:NUMBER":
                    return token
        return 0

    def find_account_references(sequence):
        refs = []
        for token, statement, tag in sequence:
            if statement == "meta:record-reference":
                if tag == "t:meta:ACCOUNT_NUMBER":
                    refs.append(token)
        return refs

    def find_father_location(sequence):
        prior_Father = False
        prior_Located_in = False
        for token, statement, tag in sequence:
            if statement == "fam:parents":
                if tag == "t:person:FATHER":
                    prior_Father = True
                    prior_Located_in = False
                elif tag == "t:person:LOCATED_IN" and prior_Father:
                    prior_Father = False
                    prior_Located_in = True
                elif tag == "t:location:NAME" and prior_Located_in:
                    return token
        return None

    def find_mother_location(sequence):
        prior_Mother = False
        prior_Located_in = False
        for token, statement, tag in sequence:
            if statement == "fam:parents":
                if tag == "t:person:MOTHER":
                    prior_Mother = True
                    prior_Located_in = False
                elif tag == "t:person:LOCATED_IN" and prior_Mother:
                    prior_Mother = False
                    prior_Located_in = True
                elif tag == "t:location:NAME" and prior_Located_in:
                    return token
        return None

    def find_parents_location(sequence):
        prior_Parents = False
        prior_Located_in = False
        for token, statement, tag in sequence:
            if statement == "fam:parents":
                if tag == "t:person:PARENTS":
                    prior_Parents = True
                    prior_Located_in = False
                elif tag == "t:person:LOCATED_IN" and prior_Parents:
                    prior_Parents = False
                    prior_Located_in = True
                elif tag == "t:location:NAME" and prior_Located_in:
                    return token
        return None