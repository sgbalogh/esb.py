import requests
import json
import urllib

class LocationNormalizer:

    def __init__(self, pelias_url="***REMOVED***"):
        self.pelias_url = pelias_url

    def find_candidates(self, search_string):
        cleaned_string = self.__first_pass(search_string)
        query = self.pelias_url + "/search?" + urllib.parse.urlencode({"text" : cleaned_string})
        r = requests.get(query).json()
        return r['features']

    def best_guess_iterate(self, search_string):
        resp = self.best_guess(search_string)
        if resp['geocoding_match']:
            return resp
        else:
            tokens = search_string.split(" ")
            for x in range(1,len(tokens)):
                phrase = " ".join(tokens[x:])
                r2 = self.best_guess(phrase)
                if r2['geocoding_match']:
                    return r2
            return resp



    def best_guess(self, search_string):
        candidates = self.find_candidates(search_string)
        if len(candidates) > 0:
            return {
                "original_string": search_string,
                "name": candidates[0]['properties']['name'],
                "id": candidates[0]['properties']['gid'],
                "country_gid": candidates[0]['properties']['country_gid'],
                "country": candidates[0]['properties']['country'],
                "geocoding_match": True
            }
        else:
            return {
                "original_string": search_string,
                "name": self.__first_pass(search_string),
                "geocoding_match": False
            }

    def __first_pass(self, search_string):
        search_tokens = search_string.split(" ")
        replacements = {
            "Ire": "Ireland",
            "Ger": "Germany",
            "Eng": "England",
            "LP": "Liverpool",
            "Co": "County"
        }
        mod_tokens = []
        for token in search_tokens:
            if token in replacements:
                mod_tokens.append(replacements[token])
            else:
                mod_tokens.append(token)
        return " ".join(mod_tokens)