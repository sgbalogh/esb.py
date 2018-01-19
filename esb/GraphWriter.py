from neo4j.v1 import GraphDatabase


class GraphWriter:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            "host",
            auth=(
                "user",
                "password"))

    def close(self):
        self._driver.close()

    def graph_insert_record(self, record):
        self.insert(self.to_cypher(record))

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(
                self._create_and_return_greeting, message)
            print(greeting)

    def insert(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self._process, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run(
            "CREATE (a:Greeting) "
            "SET a.message = $message "
            "RETURN a.message + ', from node ' + id(a)",
            message=message)
        return result.single()[0]

    @staticmethod
    def _process(tx, message):
        result = tx.run(message)
        return True

    @staticmethod
    def to_cypher(entity):
        account_id = entity['account_number']
        subject_name = entity['original']['fields']['Name']
        lines = []
        click = 1
        lines.append("CREATE (a:Person {name:\"" + subject_name + "\"})")
        lines.append(
            "MERGE (xx1:Account {account_number:\"" + account_id + "\"})")
        lines.append("CREATE (a)-[:HAS_ACCOUNT]->(xx1)")
        for k1, v1 in entity['extracted'].items():
            if k1 == "native_of_objects":
                for x in v1:
                    click = click + 1
                    key = "zza" + str(click)
                    lines.append(
                        "MERGE (" + key + ":Location {name: \"" + x['name'] + "\"})")
                    lines.append("CREATE (a)-[:IS_NATIVE_OF]->(" + key + ")")
            elif k1 == "parents":
                for parent in v1:
                    key = "a" + str(click)
                    click = click + 1
                    if isinstance(parent, dict):
                        lines.append("CREATE (" + key + ":Person)")
                        for k2, v2 in parent.items():
                            if k2 == "location":
                                lines.append(
                                    "MERGE (z" + key + ":Location {name: \"" + v2['name'] + "\"})")
                                lines.append(
                                    "CREATE (" + key + ")-[:LOCATED_AT]->(z" + key + ")")
                            elif k2 == "type":
                                if v2 == "Father":
                                    lines.append(
                                        "CREATE (a)-[:HAS_FATHER]->(" + key + ")")
                                else:
                                    lines.append(
                                        "CREATE (a)-[:HAS_MOTHER]->(" + key + ")")
                            elif k2 == "name":
                                lines.append(
                                    "SET " + key + ".name = \"" + v2 + "\"")
                            elif k2 == "status":
                                lines.append(
                                    "SET " + key + ".living_status = \"" + v2 + "\"")
            elif k1 == "children":
                if 'children' in v1:
                    for child in v1['children']:
                        click = click + 1
                        if isinstance(child, dict):
                            key = "b" + str(click)
                            for k2, v2 in child.items():
                                if k2 == "name":
                                    lines.append(
                                        "CREATE (a)-[:HAS_CHILD]->(" + key + ":Person {name:\"" + v2 + "\"})")
            elif k1 == "emigration":
                for journey in v1:
                    if 'vessel' in journey:
                        vess = journey['vessel']
                        if 'vessel' in vess:
                            click = click + 1
                            key = "ddo" + str(click)
                            lines.append(
                                "MERGE (" + key + ":Vessel {name: \"" + vess['vessel'] + "\"})")
                            lines.append(
                                "CREATE (a)-[:EMIGRATED_VIA]->(" + key + ")")
                            for origin in entity['extracted']['emig_origin']:
                                click = click + 1
                                loc_key = "aa" + key
                                lines.append(
                                    "MERGE (" + loc_key + ":Location {name: \"" + origin['name'] + "\"})")
                                lines.append(
                                    "CREATE (" + key + ")-[:VESSEL_DEPARTED_FROM]->(" + loc_key + ")")
        return "\n".join(lines)

    @staticmethod
    def old_to_cypher(entity):
        account_id = entity['account_number']
        subject_name = entity['original']['fields']['Name']
        lines = []
        click = 1
        lines.append("CREATE (a:Person {name:\"" + subject_name + "\"})")
        lines.append(
            "MERGE (xx1:Account {account_number:\"" + account_id + "\"})")
        lines.append("CREATE (a)-[:HAS_ACCOUNT]->(xx1)")
        for k1, v1 in entity['extracted'].items():
            if k1 == "native_of":
                for k2, v2 in v1.items():
                    if k2 == "location":
                        lines.append(
                            "MERGE (zz1:Location {name: \"" + v2 + "\"})")
                        lines.append("CREATE (a)-[:IS_NATIVE_OF]->(zz1)")
            elif k1 == "parents":
                for parent in v1:
                    key = "a" + str(click)
                    click = click + 1
                    if isinstance(parent, dict):
                        lines.append("CREATE (" + key + ":Person)")
                        for k2, v2 in parent.items():
                            if k2 == "location":
                                lines.append(
                                    "MERGE (z" + key + ":Location {name: \"" + v2 + "\"})")
                                lines.append(
                                    "CREATE (" + key + ")-[:LOCATED_AT]->(z" + key + ")")
                            elif k2 == "type":
                                if v2 == "Father":
                                    lines.append(
                                        "CREATE (a)-[:HAS_FATHER]->(" + key + ")")
                                else:
                                    lines.append(
                                        "CREATE (a)-[:HAS_MOTHER]->(" + key + ")")
                            elif k2 == "name":
                                lines.append(
                                    "SET " + key + ".name = \"" + v2 + "\"")
                            elif k2 == "status":
                                lines.append(
                                    "SET " + key + ".living_status = \"" + v2 + "\"")
            elif k1 == "children":
                if 'children' in v1:
                    for child in v1['children']:
                        click = click + 1
                        if isinstance(child, dict):
                            key = "b" + str(click)
                            for k2, v2 in child.items():
                                if k2 == "name":
                                    lines.append(
                                        "CREATE (a)-[:HAS_CHILD]->(" + key + ":Person {name:\"" + v2 + "\"})")
        return "\n".join(lines)
