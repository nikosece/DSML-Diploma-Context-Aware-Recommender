from geopy.distance import geodesic
import json
from collections import Counter
import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import operator
import numpy as np
import pandas as pd
import requests
import json
import pathlib


def plot_pie(sorted_data, ax):
    """Plot a pie diagram """
    values = [x[1] for x in sorted_data]
    ingredients = [x[0] for x in sorted_data]
    wedges, texts, autotexts = ax.pie(values, autopct=lambda p: f'{p:.2f}%', textprops=dict(color="w"))
    ax.legend(wedges, ingredients,
              title="Categories",
              loc="center left",
              title_fontsize=12,
              bbox_to_anchor=(1, 0, 0.5, 1),
              prop={'size': 11})
    plt.setp(autotexts, size=8, weight="bold")


def plot_box(df_new, p_name, d_name, data):
    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(20, 10), dpi=150)
    fig.suptitle('Box plots for {}'.format(p_name), fontsize=16)
    ax_list = [ax[0][0], ax[0][1], ax[0][2], ax[1][0], ax[1][1], ax[1][2]]
    value_count = df_new[d_name].value_counts()
    total = value_count.sum()
    for i in range(0, 5):
        df_new[df_new[d_name] == i][data].boxplot(ax=ax_list[i], fontsize='small')
        percentage = 100 * value_count[i] / total
        ax_list[i].set_title("Cluster {} ({:.2f} %)".format(i, percentage))
    ax[1][2].remove()
    plt.savefig(str(pathlib.Path().absolute()) + '../Plots/Cluster_' + p_name + '.png', dpi='figure')


def scale_data(data):
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data)
    return scaled_features


def kmeans(data):
    sse = []
    for k in range(1, 11):
        kmean = KMeans(init="random", n_clusters=k, n_init=10, max_iter=300, random_state=0)
        kmean.fit(data)
        sse.append(kmean.inertia_)

    kl = KneeLocator(range(1, 11), sse, curve="convex", direction="decreasing")

    kmean = KMeans(init="random", n_clusters=kl.elbow, n_init=10, max_iter=300, random_state=0)
    y = kmean.fit_predict(data)
    return y


class Functions:
    def __init__(self):
        print("Functions initialized")

    @staticmethod
    def context_clustering(df):
        keep = ['ch_Monday', 'ch_Tuesday',
                'ch_Wednesday', 'ch_Thursday', 'ch_Friday', 'ch_Saturday', 'ch_Sunday',
                'ch_Early Morning', 'ch_Morning', 'ch_Eve', 'ch_Noon', 'ch_Night',
                'ch_Late Night', 'ch_Spring', 'ch_Summer', 'ch_Fall', 'ch_Winter',
                'ch_total_ch']
        df_new = df.filter(keep)
        for i in keep[0:17]:
            df_new[i] = df_new[i] / df_new['ch_total_ch']
        names = {}
        for i in keep[0:17]:
            names[i] = i.replace("ch_", "")
        df_new = df_new.rename(columns=names)
        names = list(names.values())
        days = names[0:7]
        session = names[7:13]
        season = names[13:17]
        df_new['Day_Cluster'] = kmeans(scale_data(df_new[days]))
        df_new['Session_Cluster'] = kmeans(scale_data(df_new[session]))
        df_new['Season_Cluster'] = kmeans(scale_data(df_new[season]))
        fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(20, 10), dpi=150)
        fig.suptitle('Box plots for Days', fontsize=16)
        ax_list = [ax[0][0], ax[0][1], ax[1][0], ax[1][1]]
        value_count = df_new['Day_Cluster'].value_counts()
        total = value_count.sum()
        for i in range(0, 4):
            df_new[df_new.Day_Cluster == i][days].boxplot(ax=ax_list[i], fontsize='small')
            percentage = 100 * value_count[i] / total
            ax_list[i].set_title("Cluster {} ({:.2f} %)".format(i, percentage))
        plt.savefig(str(pathlib.Path().absolute()) + '../Plots/Cluster_Days.png', dpi='figure')
        plot_box(df_new, 'Session', 'Session_Cluster', session)
        plot_box(df_new, 'Season', 'Season_Cluster', season)
        return df_new

    @staticmethod
    def filtering_city(df, city):
        """keep only rows which city value is equal to input"""
        new_df = df[(df.city == city)].copy()
        return new_df

    @staticmethod
    def filtering_state(df, state):
        """keep only rows which state value is equal to input"""
        new_df = df[(df.state == state)]
        return new_df

    @staticmethod
    def filtering_stars(df, star):
        """keep only rows which star value is greater or equal to input"""
        new_df = df[(df.stars >= star)]
        return new_df

    @staticmethod
    def map_hour(hour):
        if hour in range(0, 5):
            return 'ch_Late Night'
        elif hour in range(5, 9):
            return 'ch_Early Morning'
        elif hour in range(9, 13):
            return 'ch_Morning'
        elif hour in range(13, 17):
            return 'ch_Noon'
        elif hour in range(17, 21):
            return 'ch_Eve'
        else:
            return 'ch_Night'

    @staticmethod
    def calculate_distance(origin, dist):
        """Calculate distance between user's location and business location.
        This distance IS NOT driving distance, it is geodesic distance"""
        # (latitude, longitude) don't confuse
        return geodesic(origin, dist).kilometers

    @staticmethod
    def calculate_distance_api(origin, df, vechile):
        """Calculate distance between user's location and business location.
        from openMap api distance can be car-driven or foot"""
        # (longitude, latitude) don't confuse
        if vechile == 0:
            post_str = 'https://api.openrouteservice.org/v2/matrix/driving-car'
        else:
            post_str = 'https://api.openrouteservice.org/v2/matrix/foot-walking'
        locations = origin
        locations.extend([[x.longtitude, x.latitude] for x in df])
        destinations = list(range(1, len(locations)))
        body = {"locations": locations, "destinations": destinations,
                "metrics": ["distance", "duration"], "sources": [0], "units": "km"}
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': '5b3ce3597851110001cf6248a22eebae30af4b398201ada78e405dba',
            'Content-Type': 'application/json; charset=utf-8'
        }
        call = requests.post(post_str, json=body, headers=headers)
        call_json = call.json()
        return call_json["distances"][0], call_json["durations"][0]

    @staticmethod
    def remove_categories(df, word):
        """As food and Restaurants not specify important information
        when they are combined with other categories, the are removed
        for better classification. """
        df.categories.replace('(^' + word + ', |, ' + word + '$)', '', regex=True, inplace=True)
        df.categories.replace(', ' + word + ',', ',', regex=True, inplace=True)
        return df

    @staticmethod
    def convert_to_json(df_b):
        """Creates a dictionary containing all of the attributes keys.
         The value of each item is either a list with all the values of the
         key, or a dictionary with all sub key-value combinations for
         that key. Businesses with missing attributes columns were
         1161. Most of them had less than 20 reviews and star
         value was less than 3, so they were removed
         This function is used ONLY WHEN reading business_R,
         as at business_R_attributes there are columns with
         all the attributes"""
        # There some jsons, that contain sub-json
        # First I will analyze the globals
        # Goal is to find a set of keys and a set
        # of values for each key
        to_json = list()
        attributes = df_b.attributes.to_list()
        for i in attributes:
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
        return pairs, to_json

    @staticmethod
    def attributes_frequency(pairs, json_file):
        """This function counts how many times a value of
         an attributed is found"""
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
        attributes are missing, i could fill them with np.nan"""
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                for i in range(len(json_file)):
                    if key not in json_file[i] or json_file[i][key] == "None" or json_file[i][key] == "none":
                        json_file[i][key] = np.nan
            else:
                for i in range(len(json_file)):
                    if key not in json_file[i] or isinstance(json_file[i][key], str):
                        to_fill = dict()
                        for sub_key in list(pairs[key].keys()):
                            to_fill[sub_key] = np.nan
                        json_file[i][key] = to_fill
                    else:
                        for sub_key in list(pairs[key].keys()):
                            if sub_key not in json_file[i][key] or json_file[i][key][sub_key] == "None":
                                json_file[i][key][sub_key] = np.nan
        return json_file

    @staticmethod
    def remove_attributes(pairs, json_file, freq):
        """Remove the attribute which None value is
        greater than 62% as they are not representative variables"""
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                percentage = (100 * freq[key]["None"]) / len(json_file)
                if percentage > 80:
                    del pairs[key]
                    del freq[key]
                    for j in json_file:
                        del j[key]
            else:
                sub_key = list(pairs[key].keys())
                sub_key = sub_key[0]
                percentage = (100 * freq[key][sub_key]["None"]) / len(json_file)
                if percentage > 80:
                    del pairs[key]
                    del freq[key]
                    for j in json_file:
                        del j[key]
        for key in list(pairs.keys()):
            if not isinstance(pairs[key], set):
                for j in json_file:
                    flag = True
                    for k in list(pairs[key].keys()):
                        if j[key][k] != "None":
                            flag = False
                            break
                    if flag:
                        j[key] = "None"
        return pairs, json_file, freq

    @staticmethod
    def fix_attribute_column(df_b):
        """This function fixed the original dateset json errors.
        After all the json were loaded and processed, they were
        transformed into str and were saved to business_R.csv
        There is NO NEED TO RUN AGAIN this function"""
        pairs, json_file = Functions.convert_to_json(df_b)
        json_file = Functions.fill_missing_keys(pairs, json_file)
        freq = Functions.attributes_frequency(pairs, json_file)
        pairs, json_file, freq = Functions.remove_attributes(pairs, json_file, freq)
        json_str = list()
        for i in range(len(json_file)):
            json_str.append(json.dumps(json_file[i]))
        df_b["attributes"] = json_str
        return pairs, json_file, freq

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
                    plt.savefig(str(pathlib.Path().absolute()) + '../Plots/attribute_plots/' + key + '.png',
                                dpi='figure')
                    plt.cla()
            else:
                for sub_key in list(pairs[key].keys()):
                    if freq[key][sub_key]["None"] < 25682:
                        sorted_data = sorted(freq[key][sub_key].items(), key=operator.itemgetter(1), reverse=True)
                        plot_pie(sorted_data, ax)
                        ax.set_title(key + " " + sub_key,
                                     fontdict={'fontsize': 20, 'fontweight': 'medium'})
                        plt.savefig(str(pathlib.Path().absolute()) + '../Plots/attribute_plots/Sub/'
                                    + key + "_" + sub_key + '.png', dpi='figure')
                        plt.cla()

    @staticmethod
    def read_business():
        return pd.read_csv(str(pathlib.Path().absolute()) +
                           '/Dataset/bussines_R_attributes.csv',
                           dtype={'name': str,
                                  'city': str, 'state': str,
                                  'latitude': float, 'longitude': float,
                                  'business_id': str, 'stars': np.float32,
                                  'categories': str,
                                  'review_count': np.int32,
                                  'RestaurantsPriceRange2': np.float16,
                                  'valet': np.float16,
                                  'street': np.float16,
                                  'validated': np.float16, 'lot': np.float16,
                                  'garage': np.float16,
                                  'RestaurantsTakeOut': np.float16,
                                  'GoodForKids': np.float16,
                                  'Caters': np.float16,
                                  'RestaurantsReservations': np.float16,
                                  'BikeParking': np.float16,
                                  'RestaurantsDelivery': np.float16,
                                  'classy': np.float16, 'romantic': np.float16,
                                  'divey': np.float16, 'hipster': np.float16,
                                  'upscale': np.float16, 'trendy': np.float16,
                                  'touristy': np.float16,
                                  'intimate': np.float16, 'casual': np.float16,
                                  'HasTV': np.float16, 'NoiseLevel': np.float16,
                                  'BusinessAcceptsCreditCards': np.float16,
                                  'RestaurantsGoodForGroups': np.float16,
                                  'latenight': np.float16, 'dessert': np.float16,
                                  'lunch': np.float16, 'dinner': np.float16,
                                  'brunch': np.float16, 'breakfast': np.float16,
                                  'OutdoorSeating': np.float16, 'WiFi': str,
                                  'RestaurantsAttire': str
                                  }, index_col='business_id')
