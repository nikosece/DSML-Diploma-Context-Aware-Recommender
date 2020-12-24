from geopy.distance import geodesic
import json
from collections import Counter
import matplotlib.pyplot as plt
import operator


def plot_pie(sorted_data, ax):
    values = [x[1] for x in sorted_data]
    ingredients = [x[0] for x in sorted_data]
    wedges, texts, autotexts = ax.pie(values, autopct=lambda p: f'{p:.2f}%', textprops=dict(color="w"))
    ax.legend(wedges, ingredients,
              title="Categories",
              loc="center left",
              title_fontsize=12,
              bbox_to_anchor=(1, 0, 0.5, 1),
              prop={'size': 11})
    plt.setp(autotexts, size=10, weight="bold")


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
        sub_j = dict()
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                c[key] = Counter(ob[key] for ob in json_file)
            else:
                sub_j[key] = [j[key] for j in json_file]
                c[key] = dict()
                for sub_key in list(pairs[key].keys()):
                    c[key][sub_key] = Counter(ob[sub_key] for ob in sub_j[key])
                    c[key] = dict(c[key])
        c = dict(c)
        return c

    @staticmethod
    def fill_missing_keys(pairs, json_file):
        """There are some businesses where where some
        attributes are missing, i could fill them with None"""
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                for i in range(len(json_file)):
                    if key not in json_file[i]:
                        json_file[i][key] = "None"
            else:
                for i in range(len(json_file)):
                    if key not in json_file[i] or isinstance(json_file[i][key], str):
                        to_fill = dict()
                        for sub_key in list(pairs[key].keys()):
                            to_fill[sub_key] = "None"
                        json_file[i][key] = to_fill
                    else:
                        for sub_key in list(pairs[key].keys()):
                            if sub_key not in json_file[i][key]:
                                json_file[i][key][sub_key] = "None"

        return json_file

    @staticmethod
    def plot_attributes(pairs, freq):
        """ Plot only attributes which None is less than 60 % """
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100, subplot_kw=dict(aspect="equal"))
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                if freq[key]["None"] < 25682:
                    sorted_data = sorted(freq[key].items(), key=operator.itemgetter(1), reverse=True)
                    plot_pie(sorted_data, ax)
                    ax.set_title(key,
                                 fontdict={'fontsize': 20, 'fontweight': 'medium'})
                    plt.savefig('/home/anonymous/Documents/Diploma-Recommender/Plots/attribute_plots/' + key + '.png',
                                dpi='figure')
                    plt.cla()
            else:
                for sub_key in list(pairs[key].keys()):
                    if freq[key][sub_key]["None"] < 25682:
                        sorted_data = sorted(freq[key][sub_key].items(), key=operator.itemgetter(1), reverse=True)
                        plot_pie(sorted_data, ax)
                        ax.set_title(key + " " + sub_key,
                                     fontdict={'fontsize': 20, 'fontweight': 'medium'})
                        plt.savefig('/home/anonymous/Documents/Diploma-Recommender/Plots/attribute_plots/Sub/'
                                    + key + "_" + sub_key + '.png', dpi='figure')
                        plt.cla()
