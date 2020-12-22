from recommender_engine import RecommenderEngine
from functions import Functions
import pandas as pd
import numpy as np


def filtering_city(df, star):
    return Functions.filtering_city(df, star)


def get_recommendations_include_rating(keywords, df):
    return RecommenderEngine.get_recommendations_include_rating(keywords, df)


# All of the below files have been filtered to contain Restaurants sub-categories
df_b = pd.read_csv('bussines_R.csv', dtype={'name': str,
                                            'city': str, 'state': str, 'postal_code': str,
                                            'latitude': float, 'longitude': float,
                                            'business_id': str, 'stars': float,
                                            'attributes': str, 'categories': str}, index_col='business_id')

# At this point there is no need to read the reviews file
# df_r = pd.read_csv("reviews_R_context.csv", dtype={'user_id': str,
#                                                    'review_stars': np.int8, 'text': str,
#                                                    'weekday': np.int8, 'season': np.int8,
#                                                    'session': str}, parse_dates=["date"], index_col='business_id')

# df_c = pd.read_csv("checkin_R.csv", dtype={'weekday': np.int8, 'season': np.int8,
#                                            'session': str}, parse_dates=["date"], index_col='business_id')
# Store all cities reverse sorted
cities = df_b.city.value_counts()
# print top 12
for i in range(0, 12):
    print(cities.index[i])
city = input("Please type city name and hit ENTER")
df_new = filtering_city(df_b, city)
df_explode = df_new.assign(categories=df_new.categories.str.split(', ')).explode('categories')
categories = df_explode.categories.value_counts()
# print top 20 categories starting from third
for i in range(2, 22):
    print(categories.index[i])
category = input("Please one or more categories with comma separated")
origin = (51.0480042, -114.0966936) # Calgary
df_new["Distance"] = df_new.apply(lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
                                  axis=1)
top_5_recommendations = get_recommendations_include_rating([category], df_new)
print("#####################################################################################")
pd.set_option('display.max_columns', None)
print(top_5_recommendations)
pd.reset_option('display.max_rows')
print("#####################################################################################")
