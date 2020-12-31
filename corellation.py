import pandas as pd
import numpy as np
import scipy.stats as ss
import seaborn as sns
import matplotlib.pyplot as plt
from kmodes.kmodes import KModes


def create_df(test1, categories):
    """This is for corellation
    between category and each attribute."""
    a = list()
    b = list()
    for i in range(len(test1)):
        if test1[i] != "None":
            a.append(categories[i])
            b.append(test1[i])
    df = pd.DataFrame()
    df["category"] = a
    return df, b


def map_attributes(value):
    """This is how attributes are mapped to
    dataframe. This has been already executed
    and business_R_attributes contains that info."""
    mapper = {"False": 0, "True": 1, "quiet": 0, "average": 1, "loud": 2, "very_loud": 3, "1": 1, "2": 2, "3": 3,
              "4": 4}
    if value in mapper:
        return mapper[value]
    else:
        return value


def cramers_v(confusion_matrix):
    """ calculate Cramers V statistic for categorical-categorical association.
        uses correction from Bergsma and Wicher,
        Journal of the Korean Statistical Society 42 (2013): 323-328
        This is used instead pearson for corellation between
        categorical variables.
    """
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))


def calculate(a, b, key1, key2):
    """This is the basic function for
    the computation of cramers_v corellation and
    it is used to find corellation between the
    attributes"""
    df = pd.DataFrame()
    df[key1] = a
    df[key2] = b
    confusion_matrix = pd.crosstab(df[key1], df[key2]).values
    result = cramers_v(confusion_matrix)
    return result


def cor_map(corr):
    f, ax = plt.subplots(figsize=(16, 15), dpi=200)
    # corr = df.corr()
    sns.heatmap(corr, vmin=-0.43, vmax=1, center=0, cmap=sns.diverging_palette(20, 220, n=200), square=True, ax=ax,
                annot=True, annot_kws={"fontsize": 6}, fmt=".2f")
    ax.set_title("Corellation between attributes and context information", fontsize=20)
    plt.show()


class Corellation:
    def __init__(self):
        print("Context create initialized")

    @staticmethod
    def attribute_to_column(pairs, json_file, df_b):
        """This was used to create a column for each one
        of the attributes. This is also not need to run again!"""
        for key in list(pairs.keys()):
            if isinstance(pairs[key], set):
                df_b[key] = [map_attributes(j[key]) for j in json_file]
            else:
                for sub_key in list(pairs[key].keys()):
                    df_b[sub_key] = [map_attributes(j[key][sub_key]) for j in json_file]
        return df_b

    @staticmethod
    def clustering(df, k=5, init='Cao', attributes=True):
        """ Create cluster based on attributes or category
        !!! dropping not common categories gives exactly
        the same cluster!!"""
        if init == 'Cao':
            n_init = 1
        else:
            n_init = 11
        if attributes:
            df2 = df.copy()
            a = list(df2.columns)
            a = a[8:42]
            df2 = df2.filter(a)
            maping = {"casual": 0, "dressy": 1, 'formal': 2}
            df2["RestaurantsAttire"] = df2.RestaurantsAttire.map(maping)
            df2 = df2.drop(
                ["BusinessAcceptsCreditCards", "RestaurantsGoodForGroups", "latenight", "OutdoorSeating", "dessert",
                 "HasTV", "intimate", "divey"], axis=1)
            df2 = df2.drop(["validated"], axis=1)
            df2 = df2.drop(["romantic"], axis=1)
            df2 = df2.drop(["NoiseLevel"], axis=1)
            df2 = df2.drop(["RestaurantsDelivery"], axis=1)
            df2 = df2.drop(["Caters", "WiFi"], axis=1)
            df2 = df2.fillna(-1)
            km = KModes(n_clusters=k, init=init, n_init=n_init, verbose=1, n_jobs=12, random_state=0)
            clusters = km.fit_predict(df2)
        else:
            df_explode = df.assign(categories=df.categories.str.split(', ')).explode('categories')
            df_explode = df_explode.filter(["categories"])
            c = df_explode.categories.value_counts()
            c = c[c > 50]
            c = c[c < 42176]
            my_keys = list(c.index)
            df2 = pd.get_dummies(df_explode)
            for i in range(len(my_keys)):
                my_keys[i] = 'categories_' + my_keys[i]
            df2 = df2.filter(my_keys)
            km = KModes(n_clusters=k, init=init, n_init=n_init, verbose=1, n_jobs=12, random_state=0)
            clusters_names = km.fit_predict(df2)
            df2["Clusters"] = clusters_names
            df2 = df2[~df2.index.duplicated(keep='first')]
            df2 = df2.filter(["Clusters"])
            clusters = df2.Clusters.to_list()
        return clusters

    @staticmethod
    def category_cor(pairs, json_file, categories):
        category_cor = dict()
        for key1 in list(pairs.keys()):
            if isinstance(pairs[key1], set):
                test1 = [j[key1] for j in json_file]
                df, b = create_df(test1, categories)
                df[key1] = b
                confusion_matrix = pd.crosstab(df["category"], df[key1]).values
                result = cramers_v(confusion_matrix)
                print("Corellation for {} was : {:.2f}".format(key1, result))
                category_cor[key1] = result
            else:
                for sub1 in list(pairs[key1].keys()):
                    test1 = [j[key1][sub1] for j in json_file]
                    df, b = create_df(test1, categories)
                    df[key1 + "_" + sub1] = b
                    confusion_matrix = pd.crosstab(df["category"], df[key1 + "_" + sub1]).values
                    result = cramers_v(confusion_matrix)
                    print("Corellation for {} was : {:.2f}".format(key1 + "_" + sub1, result))
                    category_cor[key1 + "_" + sub1] = result
        return category_cor

    @staticmethod
    def corr_attributes(pairs, json_file):
        """This function implements the computation of the
        corellation between all attributes, and it is maybe
        not so useful!"""
        corellation = dict()
        for key1 in list(pairs.keys()):
            for key2 in list(pairs.keys()):
                if key1 != key2:
                    if isinstance(pairs[key1], set):
                        if isinstance(pairs[key2], set):
                            if (key2, key1) not in corellation:
                                a = list()
                                b = list()
                                for j in json_file:
                                    if j[key1] != "None" and j[key2] != "None":
                                        a.append(j[key1])
                                        b.append(j[key2])
                                result = calculate(a, b, key1, key2)
                                corellation[(key1, key2)] = result
                        else:
                            for sub2 in list(pairs[key2].keys()):
                                if (key2 + "_" + sub2, key1) not in corellation:
                                    a = list()
                                    b = list()
                                    for j in json_file:
                                        if j[key1] != "None" and j[key2][sub2] != "None":
                                            a.append(j[key1])
                                            b.append(j[key2][sub2])
                                    if len(a) > 10:
                                        result = calculate(a, b, key1, key2 + "_" + sub2)
                                        corellation[(key1, key2 + "_" + sub2)] = result
                    else:
                        if isinstance(pairs[key2], set):
                            for sub1 in list(pairs[key1].keys()):
                                if (key2, key1 + "_" + sub1) not in corellation:
                                    a = list()
                                    b = list()
                                    for j in json_file:
                                        if j[key2] != "None" and j[key1][sub1] != "None":
                                            a.append(j[key1][sub1])
                                            b.append(j[key2])
                                    if len(a) > 10:
                                        result = calculate(a, b, key1 + "_" + sub1, key2)
                                        corellation[(key1 + "_" + sub1, key2)] = result
                        else:
                            for sub1 in list(pairs[key1].keys()):
                                for sub2 in list(pairs[key2].keys()):
                                    if (key2 + "_" + sub2, key1 + "_" + sub1) not in corellation:
                                        a = list()
                                        b = list()
                                        for j in json_file:
                                            if j[key1][sub1] != "None" and j[key2][sub2] != "None":
                                                a.append(j[key1][sub1])
                                                b.append(j[key2][sub2])
                                        if len(a) > 10:
                                            result = calculate(a, b, key1 + "_" + sub1, key2 + "_" + sub2)
                                            corellation[(key1 + "_" + sub1, key2 + "_" + sub2)] = result
        return corellation
