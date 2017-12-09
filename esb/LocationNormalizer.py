from esb.Utils import Utils

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser, OrGroup, FuzzyTermPlugin

class LocationNormalizer:
    def __init__(self):
        self.irish_entities = Utils.load_geonames_rows("./data/geonames/IE.csv")
        self.cities_over_1k_pop = Utils.load_geonames_rows("./data/geonames/cities1000.csv")
        self.schema = Schema(geonamesid=ID(stored=True), name=TEXT)
        self.ix = create_in("./data/index", self.schema)
        self.writer = self.ix.writer()
        self.geonames_dictionary = self.__create_geonames_dict()
        self.__update_index()

    def find_location(self, input_string):
        with self.ix.searcher() as searcher:
            parser = QueryParser("name", schema=self.ix.schema, group=OrGroup)
            parser.add_plugin(FuzzyTermPlugin())
            query = parser.parse(input_string)
            results = searcher.search(query)
            return results

    def __update_index(self):
        for city,idx in zip(self.cities_over_1k_pop, range(0,len(self.cities_over_1k_pop))):
            print(idx)
            id = city['geonameid']
            name = city['name'].lower()
            self.writer.add_document(geonamesid=id, name=name)
        self.writer.commit()

    def __create_geonames_dict(self):
        d = {}
        for x in self.cities_over_1k_pop + self.irish_entities:
            d[x['geonameid']] = x
        return d
