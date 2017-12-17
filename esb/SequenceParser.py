from esb import ParseTree
from esb.Rules import Rules
from esb.Tags import Tags
from queue import Queue

from esb.Triple import Triple
# from dateutil import parser as dp

class SequenceParser:

    @staticmethod
    def discretize_tree(parse_tree):
        results = {}
        for theme in parse_tree.children:
            if theme.label == Tags.Thematic.FAM_PARENTS:
                results['parents'] = SequenceParser.discretize_parents(theme)
            elif theme.label == Tags.Thematic.SUBJ_EMIGRATION:
                results['emigration'] = SequenceParser.discretize_emigration(theme)
            elif theme.label == Tags.Thematic.FAM_SIBLINGS:
                continue
            elif theme.label == Tags.Thematic.META_RECORD:
                results['references'] = SequenceParser.discretize_references(theme)
            elif theme.label == Tags.Thematic.SUBJ_NATIVEOF:
                results['nativity'] = SequenceParser.discretize_nativity(theme)
        return results

    @staticmethod
    ## this methods seems to work; it's the only one using DFS at the moment
    def discretize_references(root_node):
        if root_node.label == Tags.Thematic.META_RECORD:
            return SequenceParser.dfs(root_node, Tags.Token.META_ACCOUNT_NUMBER)

    @staticmethod
    def dfs(root_node, search_label):
        results = []
        for x in root_node.children:
            results = results + SequenceParser.dfs_visit(x, search_label)
        return results

    @staticmethod
    def dfs_visit(start_node, search_label):
        to_return = []
        start_node.dfs_color = "gray"
        for x in start_node.children:
            if x.dfs_color == "white":
                x.dfs_parent = start_node
                if x.label == search_label:
                    to_return.append(x.token)
                else:
                    to_return = to_return + SequenceParser.dfs_visit(x, search_label)
        start_node.dfs_color = "black"
        return to_return



    @staticmethod
    ## unclear if this method is achieving 100% recall of parse trees
    def discretize_nativity(root_node):
        if root_node.label == Tags.Thematic.SUBJ_NATIVEOF:
            record = {

            }
            for child in root_node.children:
                if child.label == Rules.NATIVE_OF_START:
                    for grandchild in child.children:
                        if grandchild.label == Tags.Token.LOCATION_NAME:
                            record['name'] = grandchild.token
            return [record]

    @staticmethod
    ## this method is NOT reading parse trees with 100% recall (see records[1174])
    def discretize_emigration(root_node):
        if root_node.label == Tags.Thematic.SUBJ_EMIGRATION:
            record = {
                "date" : {},
                "vessel" : {}
            }
            for child in root_node.children:
                if child.label == Rules.EMIGRATION_START:
                    for grandchild in child.children:
                        if grandchild.label == Rules.EMIGRATION_DATE:
                            for greatgrandchild in grandchild.children:
                                if greatgrandchild.label == Tags.Token.TIME_MONTH:
                                    record['date']['month'] = greatgrandchild.token
                                elif greatgrandchild.label == Tags.Token.TIME_DATE:
                                    record['date']['date'] = greatgrandchild.token
                                elif greatgrandchild.label == Tags.Token.TIME_YEAR:
                                    record['date']['year'] = greatgrandchild.token
                        if grandchild.label == Rules.EMIGRATION_VESSEL:
                            prev_label_was_VESSEL_HAS_ORIGIN: False
                            for greatgrandchild in grandchild.children:
                                if greatgrandchild.label == Tags.Token.EMIGRATION_VESSEL:
                                    record['vessel']['name'] = greatgrandchild.token
                                    prev_label_was_VESSEL_HAS_ORIGIN = False
                                if greatgrandchild.label == Tags.Token.EMIGRATION_VESSEL_HAS_ORIGIN:
                                    prev_label_was_VESSEL_HAS_ORIGIN = True
                                if greatgrandchild.label == Tags.Token.LOCATION_NAME:
                                    if prev_label_was_VESSEL_HAS_ORIGIN:
                                        record['vessel']['origin'] = greatgrandchild.token
            return [record]




    @staticmethod
    ## this method is NOT reading parse trees with 100% recall (see records[1174])
    def discretize_parents(root_node):
        if root_node.label == Tags.Thematic.FAM_PARENTS:
            collection = []
            for child in root_node.children:
                SequenceParser.find_parent(child, collection)
            ## merg
            both = []
            consolidated = []
            for parent in collection:
                if parent['type'] == "BOTH":
                    for k,v in parent.items():
                        if k != "type":
                            both.append({k: v})
            if len(both) > 0:
                for parent in collection:
                    if parent['type'] != "BOTH":
                        for d in both:
                            parent.update(d)
                        consolidated.append(parent)
                return consolidated
            else:
                return collection

    @staticmethod
    def find_parent(node, collection):
        ## called on a parent_start node
        if node.label is Rules.PARENT_START:
            record = {}
            for child in node.children:
                if child.label == Rules.PARENT_TYPE:
                    for grandchild in child.children:
                        if grandchild.label == Tags.Token.PERSON_FATHER:
                            record['type'] = "FATHER"
                        elif grandchild.label == Tags.Token.PERSON_MOTHER:
                            record['type'] = "MOTHER"
                        elif grandchild.label == Tags.Token.PERSON_PARENTS:
                            record['type'] = "BOTH"
                elif child.label == Rules.PARENT_LOCATION:
                    for grandchild in child.children:
                        if grandchild.label == Tags.Token.LOCATION_NAME:
                            record['located_in'] = grandchild.token
                elif child.label == Rules.PARENT_STATUS:
                    for grandchild in child.children:
                        if grandchild.label == Tags.Token.PERSON_IS_DEAD:
                            record['status'] = "dead"
                        elif grandchild.label == Tags.Token.PERSON_IS_LIVING:
                            record['status'] = "alive"
                elif child.label == Tags.Token.PERSON_NAME:
                    record['name'] = child.token
                elif child.label == Rules.PARENT_START:
                    SequenceParser.find_parent(child, collection)
            collection.append(record)


    @staticmethod
    def create_parse_tree(labeled_record):
        stmt_lists, token_lists, remarks_lists = SequenceParser.split_lists_by_stmt_labels(labeled_record.statement_labels,
                                                                                           labeled_record.token_labels,
                                                                            [item[0] for item in labeled_record.remarks_labels])

        record_root_node = ParseTree.TreeNode(labeled_record.row['Name'])
        for label_idx in range(len(stmt_lists)):
            label_tag = stmt_lists[label_idx][0]
            if label_tag in Rules.Rules.ignored_tags:
                continue
            label_rules = Rules.Rules.get_rules_by_tag(label_tag)
            label_root_node = SequenceParser.get_root_from_parse_tree(token_lists[label_idx], remarks_lists[label_idx], label_tag,
                                                       label_rules)
            record_root_node.children.append(label_root_node)
        return record_root_node

    @staticmethod
    def get_root_from_parse_tree(tokens, remarks, tag_name, rules):
        root = ParseTree.TreeNode(tag_name)
        nodes = list()
        for idx in range(len(tokens)):
            token_tag = tokens[idx]
            token = remarks[idx]
            nodes.append(ParseTree.TreeNode(token_tag, token))
        while True:
            updated_tokens, updated_remarks, updated_nodes = Rules.parse_tree_by_label(rules, tokens, remarks, nodes)
            if len(updated_tokens) == len(tokens) and updated_tokens == tokens:
                # add the rest of the unattached nodes to root
                for node in nodes:
                    root.children.append(node)
                break
            else:
                tokens = updated_tokens
                nodes = updated_nodes
        return root

    @staticmethod
    def split_lists_by_stmt_labels(stmt_labels, token_labels, remarks_labels):
        if (len(stmt_labels) != len(token_labels) and len(token_labels) != len(remarks_labels)) or len(
                stmt_labels) == 0:
            return None
        output_stmt_labels = []
        output_token_labels = []
        output_remarks_labels = []
        prev_label_idx = 0
        prev_label = stmt_labels[prev_label_idx]

        for idx in range(1, len(stmt_labels)):

            label = stmt_labels[idx]

            if label != prev_label:
                output_stmt_labels.append(stmt_labels[prev_label_idx:idx])
                output_token_labels.append(token_labels[prev_label_idx:idx])
                output_remarks_labels.append(remarks_labels[prev_label_idx:idx])
                prev_label_idx = idx
                prev_label = label

        output_stmt_labels.append(stmt_labels[prev_label_idx:])
        output_token_labels.append(token_labels[prev_label_idx:])
        output_remarks_labels.append(remarks_labels[prev_label_idx:])
        return output_stmt_labels, output_token_labels, output_remarks_labels

    @staticmethod
    def parse_siblings_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.FAM_SIBLINGS:
            return None

        siblings_record = []
        siblings_type = None

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.SIBLINGS_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when SIBLINGS_START
                        if node.label == Rules.SIBLINGS_START:
                            siblings_type = None

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set siblings_type variable when reached SIBLINGS_TYPE
                        elif node.label == Rules.SIBLINGS_TYPE:

                            for child_node in node.children:

                                if child_node.label == Tags.Token.PERSON_BROTHERS:
                                    siblings_type = "BROTHERS"

                                elif child_node.label == Tags.Token.PERSON_SISTERS:
                                    siblings_type = "SISTERS"

                        # Create a siblings entity when reached SIBLINGS_NAME
                        elif node.label == Rules.SIBLINGS_NAME:
                            sibling = dict()
                            sibling['type'] = siblings_type

                            for child_node in node.children:
                                if child_node.label == Tags.Token.PERSON_NAME:
                                    sibling['name'] = child_node.token

                                elif child_node.label == Tags.Token.META_PARENTHETICAL:
                                    sibling['parenthetical'] = child_node.token

                                elif child_node.label == Rules.SIBLINGS_LOCATION:

                                    for location_child_node in child_node.children:

                                        if location_child_node.label == Tags.Token.LOCATION_NAME:
                                            sibling['location'] = location_child_node.token

                            siblings_record.append(sibling)

            else:
                siblings_record.append(subtree_node.token)

        return siblings_record

    @staticmethod
    def parse_parents_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.FAM_PARENTS:
            return None

        parents_record = []
        parent_type = None
        parent_status = None
        parent_location = None

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.PARENT_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when PARENT_START
                        if node.label == Rules.PARENT_START:
                            parent_type = None
                            parent_status = None
                            parent_location = None

                            for parents_start_child_node in node.children:
                                queue.put(parents_start_child_node)

                        # Set parent_type variable when reached PARENT_TYPE
                        elif node.label == Rules.PARENT_TYPE:

                            for child_node in node.children:
                                if child_node.label == Tags.Token.PERSON_FATHER:
                                    parent_type = "Father"
                                elif child_node.label == Tags.Token.PERSON_MOTHER:
                                    parent_type = "Mother"
                                elif child_node.label == Tags.Token.PERSON_PARENTS:
                                    parent_type = "Both"

                        # Set parent_status variable when reached PARENT_STATUS
                        elif node.label == Rules.PARENT_STATUS:

                            for child_node in node.children:
                                if child_node.label == Tags.Token.PERSON_IS_DEAD:
                                    parent_status = "Dead"

                                elif child_node.label == Tags.Token.PERSON_IS_LIVING:
                                    parent_status = "Alive"

                        # Set parent_location variable when reached PARENT_LOCATION
                        elif node.label == Rules.PARENT_LOCATION:

                            for location_child_node in node.children:

                                if location_child_node.label == Tags.Token.LOCATION_NAME:
                                    parent_location = location_child_node.token

                        # Create a parent entity when reached PERSON_NAME
                        elif node.label == Tags.Token.PERSON_NAME:
                            parent = dict()

                            if parent_type is not None:
                                parent['type'] = parent_type

                            if parent_status is not None:
                                parent['status'] = parent_status
                            if parent_location is not None:
                                parent['location'] = parent_location

                            parent['name'] = node.token

                            parents_record.append(parent)

            else:
                parents_record.append(subtree_node.token)

        return parents_record

    @staticmethod
    def parse_emigration_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_EMIGRATION:
            return None

        emigration_record = []
        emigration = dict()

        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.EMIGRATION_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when EMIGRATION_START
                        if node.label == Rules.EMIGRATION_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Pass when reached EMIGRATION_ARRIVED
                        elif node.label == Tags.Token.EMIGRATION_ARRIVED:
                            pass

                        # Set location when reached LOCATION_NAME
                        elif node.label == Tags.Token.LOCATION_NAME:
                            emigration['location'] = node.token

                        # Set date when reached EMIGRATION_DATE
                        elif node.label == Rules.EMIGRATION_DATE:
                            emigration_date = dict()

                            for child_node in node.children:
                                if child_node.label == Tags.Token.TIME_MONTH:
                                    emigration_date['month'] = child_node.token

                                elif child_node.label == Tags.Token.TIME_YEAR:
                                    emigration_date['year'] = child_node.token

                                elif child_node.label == Tags.Token.TIME_DATE:
                                    emigration_date['date'] = child_node.token

                            emigration['date'] = emigration_date

                        # Pass when reached EMIGRATION_VIA
                        elif node.label == Tags.Token.EMIGRATION_VIA:
                            pass

                        # Set vessel when reached EMIGRATION_VESSEL
                        elif node.label == Rules.EMIGRATION_VESSEL:
                            emigration_vessel = dict()

                            for child_node in node.children:

                                if child_node.label == Tags.Token.EMIGRATION_VESSEL:
                                    emigration_vessel['vessel'] = child_node.token

                                elif child_node.label == Tags.Token.EMIGRATION_VESSEL_HAS_ORIGIN:
                                    pass

                                elif child_node.label == Tags.Token.LOCATION_NAME:
                                    emigration_vessel['location'] = child_node.token

                            emigration['vessel'] = emigration_vessel
                            emigration_record.append(emigration)

            else:
                misc.append(subtree_node.token)

            if len(misc) > 0:
                emigration_record.append(misc)

        return emigration_record

    @staticmethod
    def parse_children_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.FAM_CHILDREN:
            return None

        children_record = dict()
        children = []
        misc = []

        children_gender = None

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.CHILDREN_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when CHILDREN_START
                        if node.label == Rules.CHILDREN_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        if node.label == Tags.Token.PERSON_NUMBER:
                            children_record['count'] = node.token

                        elif node.label == Tags.Token.PERSON_SON:
                            children_gender = "Male"

                        # Append children_name into children_record when reached CHILDREN_NAME
                        elif node.label == Rules.CHILDREN_NAME:
                            child = dict()

                            for child_node in node.children:

                                # Child name
                                if child_node.label == Tags.Token.PERSON_NAME:
                                    child['name'] = child_node.token

                                # Child location
                                elif child_node.label == Rules.CHILDREN_LOCATION:

                                    for child_location_node in child_node.children:

                                        if child_location_node.label == Tags.Token.REL_IS_NATIVE_OF:
                                            pass

                                        elif child_location_node.label == Tags.Token.LOCATION_NAME:
                                            child['location'] = child_location_node.token

                            if children_gender is not None:
                                child['gender'] = children_gender

                            children.append(child)

            else:
                # unknown tags
                for child_node in subtree_node.children:
                    misc.append(child_node.token)

        if len(children) > 0:
            children_record['children'] = children

        if len(misc) > 0:
            children_record['misc'] = misc

        return children_record

    @staticmethod
    def parse_spouse_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.FAM_SPOUSE:
            return None

        spouse_record = []
        spouse_relation = None

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.SPOUSE_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when SPOUSE_START
                        if node.label == Rules.SPOUSE_START:

                            spouse_relation = None

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set spouse_relation variable when SPOUSE_RELATION
                        elif node.label == Rules.SPOUSE_RELATION:

                            for child_node in node.children:

                                if child_node.label == Tags.Token.REL_HAS_HUSBAND:
                                    spouse_relation = "Husband"

                                elif child_node.label == Tags.Token.REL_HAS_WIFE:
                                    spouse_relation = "Wife"

                                elif child_node.label == Tags.Token.REL_HAS_SPOUSE:
                                    spouse_relation = "Spouse"

                                elif child_node.label == Tags.Token.REL_IS_WIDOW_OF:
                                    spouse_relation = "Widow"

                        # Create a spouse entity when reached SPOUSE_PERSON
                        elif node.label == Rules.SPOUSE_PERSON:
                            spouse = dict()

                            if spouse_relation is not None:
                                spouse['relation'] = spouse_relation

                            for child_node in node.children:

                                if child_node.label == Tags.Token.PERSON_NAME:
                                    spouse['name'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_IS_DEAD:
                                    spouse['is_dead'] = child_node.token

                                elif child_node.label == Rules.SPOUSE_DURATION:
                                    year = str
                                    duration_year = str

                                    for duration_node in child_node.children:

                                        if duration_node.label == Tags.Token.TIME_YEAR:
                                            year = duration_node.token

                                        elif duration_node.label == Tags.Token.TIME_DURATION_YEAR:
                                            duration_year = duration_node.token

                                    spouse['duration'] = str(year) + str(duration_year)

                                elif child_node.label == Rules.SPOUSE_LOCATION:

                                    for location_node in child_node.children:

                                        if location_node.label == Tags.Token.PERSON_LOCATED_IN:
                                            pass
                                        elif location_node.label == Tags.Token.LOCATION_NAME:
                                            spouse['location'] = location_node.token

                            spouse_record.append(spouse)

            else:
                spouse_record.append(subtree_node.token)

        return spouse_record

    @staticmethod
    def parse_record_reference_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.META_RECORD:
            return None

        account_record = []
        accounts = []
        see_ref = None
        is_same_as_ref = None

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.REF_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when REF_START
                        if node.label == Rules.REF_START:

                            see_ref = None
                            is_same_as_ref = None

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set see_ref variable when META_SEE
                        elif node.label == Tags.Token.META_SEE:
                            see_ref = node.token

                        # Set is_same_as_ref variable when META_IS_SAME_AS
                        elif node.label == Tags.Token.META_IS_SAME_AS:
                            is_same_as_ref = node.token

                        # Create a ref_account entity when reached REF_ACCOUNT
                        elif node.label == Rules.REF_ACCOUNT:
                            account = dict()

                            if see_ref is not None:
                                account['see'] = see_ref

                            if is_same_as_ref is not None:
                                account['is_same'] = is_same_as_ref

                            for child_node in node.children:

                                if child_node.label == Tags.Token.META_ACCOUNT_NUMBER:
                                    account['account'] = child_node.token

                            accounts.append(account)

            else:
                account_record.append(subtree_node.token)

        if len(accounts) > 0:
            account_record.append(accounts)

        return account_record

    @staticmethod
    def parse_age_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_AGE:
            return None

        age_record = dict()
        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.AGE_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when AGE_START
                        if node.label == Rules.AGE_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set when PERSON_AGE_YEAR
                        elif node.label == Tags.Token.PERSON_AGE_YEAR:
                            age_record['age'] = node.token

                        # Set when PERSON_AGE
                        elif node.label == Tags.Token.PERSON_AGE:
                            pass

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            age_record['misc'] = misc

        return age_record

    @staticmethod
    def parse_bio_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_BIO:
            return None

        bio_record = dict()
        time = None
        year = None
        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.BIO_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when BIO_START
                        if node.label == Rules.BIO_START:
                            time = None
                            year = None

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set when TIME_DURATION_VALUE
                        elif node.label == Tags.Token.TIME_DURATION_VALUE:
                            time = node.token

                        # Set when TIME_DURATION_YEAR
                        elif node.label == Tags.Token.TIME_DURATION_YEAR:
                            year = node.token

                        # Pass when PERSON_LOCATED_IN
                        elif node.label == Tags.Token.PERSON_LOCATED_IN:
                            pass

                        # Set when LOCATION_NAME
                        elif node.label == Tags.Token.LOCATION_NAME:
                            bio_record['location'] = node.token

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            bio_record['misc'] = misc

        if time is not None and year is not None:
            bio_record['duration'] = '{} {}'.format(str(time), str(year))

        return bio_record

    @staticmethod
    def parse_martial_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_MARTIAL:
            return None

        martial_record = dict()
        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.MARITAL_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when MARITAL_START
                        if node.label == Rules.MARITAL_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Set when PERSON_IS_SINGLE
                        elif node.label == Tags.Token.PERSON_IS_SINGLE:
                            martial_record['status'] = node.token

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            martial_record['misc'] = misc

        return martial_record

    @staticmethod
    def parse_native_of_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_NATIVEOF:
            return None

        native_record = dict()
        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.NATIVE_OF_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when NATIVE_OF_START
                        if node.label == Rules.NATIVE_OF_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Pass when REL_IS_NATIVE_OF
                        elif node.label == Tags.Token.REL_IS_NATIVE_OF:
                            pass

                        # Set when LOCATION_NAME
                        elif node.label == Tags.Token.LOCATION_NAME:
                            native_record['location'] = node.token

                        # Set when NATIVE_OF_DIST
                        elif node.label == Rules.NATIVE_OF_DIST:

                            distance_info = dict()
                            distance = str
                            distance_unit = str

                            for child_node in node.children:

                                if child_node.label == Tags.Token.LOCATION_DISTANCE:
                                    distance = child_node.token

                                elif child_node.label == Tags.Token.LOCATION_DISTANCE_UNIT:
                                    distance_unit = child_node.token

                                elif child_node.label == Tags.Token.LOCATION_FROM:
                                    pass

                                elif child_node.label == Tags.Token.LOCATION_NAME:
                                    distance_info['from'] = child_node.token

                            distance_info['distance'] = '{} {}'.format(str(distance), str(distance_unit))
                            native_record['distance_from'] = distance_info

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            native_record['misc'] = misc

        return native_record

    @staticmethod
    def parse_occupation_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_OCCUPATION:
            return None

        occupation_record = dict()
        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.OCCUPATION_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when OCCUPATION_START
                        if node.label == Rules.OCCUPATION_START:

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        # Pass when WORK_WORKS_FOR
                        elif node.label == Tags.Token.WORK_WORKS_FOR:
                            pass

                        # Set when WORK_EMPLOYER_NAME
                        elif node.label == Tags.Token.WORK_EMPLOYER_NAME:
                            occupation_record['employer'] = node.token

                        # Set when WORK_OCCUPATION
                        elif node.label == Tags.Token.WORK_OCCUPATION:
                            occupation_record['occupation'] = node.token

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            occupation_record['misc'] = misc

        return occupation_record

    @staticmethod
    def parse_residence_subtree(subtree_root):
        if subtree_root is None or subtree_root.label != Tags.Thematic.SUBJ_RESIDENCE:
            return None

        residence_record = dict()
        reside_with = None
        reside_location = None
        reside_people = []

        misc = []

        for subtree_node in subtree_root.children:

            if subtree_node.label == Tags.Token.BLANK:
                continue

            if subtree_node.label == Rules.RESIDENTIAL_START:

                # BFS
                queue = Queue()
                queue.put(subtree_node)

                while not queue.empty():
                    size = queue.qsize()

                    for remain_node_count in range(size):
                        node = queue.get()

                        # Put all nodes into queue when RESIDENTIAL_START
                        if node.label == Rules.RESIDENTIAL_START:
                            reside_with = None
                            reside_location = None

                            for sib_start_child_node in node.children:
                                queue.put(sib_start_child_node)

                        elif node.label == Tags.Token.RESIDENTIAL_LIVES_WITH:
                            reside_with = node.token

                        elif node.label == Tags.Token.RESIDENTIAL_LIVED_WITH:
                            reside_with = node.token

                        elif node.label == Tags.Token.RESIDENTIAL_CURRENTLY_LIVING_AT:
                            pass

                        elif node.label == Tags.Token.RESIDENTIAL_FORMERLY_LOCATED_AT:
                            pass

                        elif node.label == Rules.RESIDENTIAL_LOCATION:

                            for child_node in node.children:

                                if child_node.label == Tags.Token.LOCATION_NAME:
                                    reside_location = child_node.token
                                    residence_record['location'] = reside_location

                        elif node.label == Rules.RESIDENTIAL_PERSON:

                            person = dict()
                            if reside_with is not None:
                                person['reside_with'] = reside_with

                            if reside_location is not None:
                                person['location'] = reside_location

                            for child_node in node.children:

                                if child_node.label == Tags.Token.PERSON_NAME:
                                    person['name'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_SON:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_MOTHER:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_FATHER:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_BROTHERS:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_SISTERS:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_WIFE:
                                    person['relation'] = child_node.token

                                elif child_node.label == Tags.Token.PERSON_CHILDREN:
                                    person['relation'] = child_node.token

                            reside_people.append(person)

            else:
                misc.append(subtree_node.token)

        if len(misc) > 0:
            residence_record['misc'] = misc

        return residence_record


