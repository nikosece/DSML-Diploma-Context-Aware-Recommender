from geopy.distance import geodesic
import json
from collections import Counter
from pprint import pprint as pp


class Functions:
    def __init__(self):
        print("Functions initialized")

    @staticmethod
    def filtering_city(df, city):
        new_df = df[(df.city == city)]
        return new_df

    @staticmethod
    def filtering_state(df, state):
        new_df = df[(df.state == state)]
        return new_df

    @staticmethod
    def filtering_stars(df, star):
        new_df = df[(df.stars >= star)]
        return new_df

    @staticmethod
    def calculate_distance(origin, dist):
        # (latitude, longitude) don't confuse
        return geodesic(origin, dist).kilometers

    @staticmethod
    def remove_categories(df):
        """As food and Restaurants not specify important information
        when they are combined with other categories, the are removed
        for better classification"""
        df.categories.replace('(^Food, |, Food$)', '', regex=True, inplace=True)
        df.categories.replace(', Food,', ',', regex=True, inplace=True)
        df.categories.replace('(^Restaurants, |, Restaurants$)', '', regex=True, inplace=True)
        df.categories.replace(', Restaurants,', ',', regex=True, inplace=True)
        return df

    @staticmethod
    def convert_to_json(df_b):
        """Creates a dictionary containing all of the attributes keys.
         The value of each item is either a list with all the values of the
         key, or a dictionary with all sub key-value combinations for
         that key."""
        # There some jsons, that contain sub-json
        # First I will analyze the globals
        # Goal is to find a set of keys and a set
        # of values for each key
        to_json = list()
        attributes = df_b.attributes.to_list()
        for i in attributes:
            if i != "" and i != " ":
                to_json.append(json.loads(i))
        json_keys = [list(i.keys()) for i in to_json]
        keys_set = [set(i) for i in json_keys]
        keys_set = set.union(*keys_set)
        pairs = {key: set() for key in keys_set}
        double_keys = set()
        for j in to_json:
            for key in keys_set:
                if key in j:
                    if isinstance(j[key], str):
                        if key not in double_keys:
                            pairs[key].add(j[key])
                    else:
                        double_keys.add(key)
                        if isinstance(pairs[key], set):
                            pairs[key] = [j[key]]
                        else:
                            pairs[key].append(j[key])
        for key in double_keys:
            json_keys = [list(i.keys()) for i in pairs[key]]
            keys_set = [set(i) for i in json_keys]
            keys_set = set.union(*keys_set)
            sub_pairs = {key: set() for key in keys_set}
            for j in pairs[key]:
                for sub_key in keys_set:
                    if sub_key in j:
                        sub_pairs[sub_key].add(j[sub_key])
            pairs[key] = sub_pairs
        return pairs

    @staticmethod
    def attributes_frequency(pairs, json_file):
        c = dict()
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                sub_j = list()
                for tr in json_file:
                    if key in tr:
                        sub_j.append(tr)
                c[key] = Counter(ob[key] for ob in sub_j)

        c = dict(c)
        return c

    # @staticmethod
    # def fill_missing_keys(pairs, json_file):
    #     """There are some businesses where where some
    #     attributes are missing, i could fill them with None"""
    #     for key in list(pairs.keys()):
    #         if isinstance(pairs[key], set):
    #             for i in range(len(json_file)):
    #                 if key not in json_file[i]:
    #                     json_file[i][key] = "None"
    #         else:
    #             for i in range(len(json_file)):
    #                 if key not in json_file[i]:
    #                     fill = dict()
    #                     for sub_key in list(pairs[key].keys()):
    #                         fill[sub_key] = "None"
    #                     json_file[i][key] = fill
    #                 else:
    #                     for sub_key in list(pairs[key].keys()):
    #                         if sub_key not in json_file[i][key]:
    #                             try:
    #                                 json_file[i][key][sub_key] = "None"
    #                             except:
    #                                 print(key, sub_key)
    #                                 print(type(json_file[i][key]))
    #                                 print(json_file[i][key])
    #                                 break
    #     return json_file
