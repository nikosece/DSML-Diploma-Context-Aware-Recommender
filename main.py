from datetime import datetime

from recommender_engine import RecommenderEngine
import json
import pandas as pd
import numpy as np

greek_keywords = "greek greece feta souvlaki gyros tzatziki athens "
nightlife_keywords = "nightclub nightclubs nightlife bar bars pub pubs party beer"


def categorize(top=10, category=False):
    df_explode = df_b.assign(categories=df_b.categories.str.split(', ')).explode('categories')["categories"]
    print("There are the top {} categories".format(top))
    print(df_explode.value_counts(normalize=True).nlargest(top))
    if category:
        a = input("Please specify category string")
        print("{} selected".format(a))
        df_b_specific = df_b[df_b['categories'].str.contains(a, na=False)]
    else:
        for val, cnt in df_explode.value_counts(normalize=True).nlargest(1).iteritems():
            print("{} selected".format(val))
            df_b_specific = df_b[df_b['categories'].str.contains(val, na=False)]
    df_r_specific = df_r[df_r['business_id'].isin(df_b_specific.index)]
    return df_b_specific, df_r_specific


def to_date(str_date):
    result = list()
    str_result = str_date.split(",")
    for i in str_result:
        if i[0] == " ":
            result.append(datetime.datetime.strptime(i[1:], '%Y-%m-%d %H:%M:%S'))
        else:
            result.append(datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S'))
    return result


def get_recommendations_include_rating(keywords, df, df2):
    return RecommenderEngine.get_recommendations_include_rating(keywords, df, df2)


def get_top_5_city_names_out_of_json(json_string):
    list_var = json.loads(json_string)
    result = []
    max_var = len(list_var)
    i = 0
    while i < max_var:
        result.append((list_var[i]['Name'], list_var[i]['score']))
        i += 1

    return result


df_b = pd.read_csv('bussines.csv', dtype={'name': str,
                                          'city': str, 'state': str, 'postal_code': str,
                                          'latitude': float, 'longitude': float,
                                          'business_id': str, 'stars': float,
                                          'attributes': str, 'categories': str}, index_col='business_id')
df_r = pd.read_csv("reviews_R_context.csv", dtype={'user_id': str,"session": str,"season":np.int8,
                                                 'business_id': str, 'review_stars': np.int8, "weekday":np.int8,
                                                   'text': str}, parse_dates=["date"], index_col='user_id')

# Version 2 requests are below:

bus, b = categorize()
top_5_cultural_with_rating = get_recommendations_include_rating(greek_keywords, b, bus)
city_names_for_cultural_rating = get_top_5_city_names_out_of_json(top_5_cultural_with_rating)
print(city_names_for_cultural_rating)
print("#################")
# df_c['test'] = df_c.apply(lambda row : to_date(row['date']), axis = 1)

### 2013-04-11 18:36:15