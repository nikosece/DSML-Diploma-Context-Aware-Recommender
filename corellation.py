import pandas as pd
import numpy as np
import scipy.stats as ss


def cramers_v(confusion_matrix):
    """ calculate Cramers V statistic for categorical-categorical association.
        uses correction from Bergsma and Wicher,
        Journal of the Korean Statistical Society 42 (2013): 323-328
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
    df = pd.DataFrame()
    df[key1] = a
    df[key2] = b
    confusion_matrix = pd.crosstab(df[key1], df[key2]).values
    result = cramers_v(confusion_matrix)
    return result


class Corellation:
    def __init__(self):
        print("Context create initialized")

    @staticmethod
    def category_cor(pairs, json_file, categories):
        category_cor = dict()
        for key1 in list(pairs.keys()):
            if isinstance(pairs[key1], set):
                test1 = [j[key1] for j in json_file]
                a = list()
                b = list()
                for i in range(len(test1)):
                    if test1[i] != "None":
                        a.append(categories[i])
                        b.append(test1[i])
                df = pd.DataFrame()
                df["category"] = a
                df[key1] = b
                confusion_matrix = pd.crosstab(df["category"], df[key1]).values
                result = cramers_v(confusion_matrix)
                print("Corellation for {} was : {:.2f}".format(key1, result))
                category_cor[key1] = result
            else:
                for sub1 in list(pairs[key1].keys()):
                    test1 = [j[key1][sub1] for j in json_file]
                    a = list()
                    b = list()
                    for i in range(len(test1)):
                        if test1[i] != "None":
                            a.append(categories[i])
                            b.append(test1[i])

                    df = pd.DataFrame()
                    df["category"] = a
                    df[key1 + "_" + sub1] = b
                    confusion_matrix = pd.crosstab(df["category"], df[key1 + "_" + sub1]).values
                    result = cramers_v(confusion_matrix)
                    print("Corellation for {} was : {:.2f}".format(key1 + "_" + sub1, result))
                    category_cor[key1 + "_" + sub1] = result
        return category_cor

    @staticmethod
    def corr_attributes(pairs, json_file):
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
