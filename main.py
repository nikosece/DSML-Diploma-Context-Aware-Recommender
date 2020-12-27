from recommender_engine import RecommenderEngine
from functions import Functions
import pandas as pd
import numpy as np
from corellation import Corellation


def filtering_city(df, star):
    return Functions.filtering_city(df, star)


def get_recommendations_include_rating(keywords, df):
    return RecommenderEngine.get_recommendations_include_rating(keywords, df)


# All of the below files have been filtered to contain Restaurants sub-categories
cols = list(range(0, 4)) + list(range(5, 8)) + list(range(9, 50))
df_b = pd.read_csv('bussines_R_attributes.csv', usecols=cols, dtype={'name': str,
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
                                                                     'RestaurantsTableService': np.float16,
                                                                     'RestaurantsTakeOut': np.float16,
                                                                     'GoodForKids': np.float16,
                                                                     'Caters': np.float16,
                                                                     'RestaurantsReservations': np.float16,
                                                                     'HappyHour': np.float16,
                                                                     'WheelchairAccessible': np.float16,
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
                                                                     'DogsAllowed': np.float16,
                                                                     'latenight': np.float16, 'dessert': np.float16,
                                                                     'lunch': np.float16, 'dinner': np.float16,
                                                                     'brunch': np.float16, 'breakfast': np.float16,
                                                                     'OutdoorSeating': np.float16,
                                                                     'Alcohol': str, 'WiFi': str,
                                                                     'RestaurantsAttire': str
                                                                     }, index_col='business_id')


# At this point there is no need to read the reviews file
# df_r = pd.read_csv("reviews_R_context.csv", dtype={'user_id': str,
#                                                    'review_stars': np.float16, 'text': str,
#                                                    'weekday': np.float16, 'season': np.float16,
#                                                    'session': str}, parse_dates=["date"], index_col='business_id')

# df_c = pd.read_csv("checkin_R.csv", dtype={'weekday': np.float16, 'season': np.float16,
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
origin = (51.0480042, -114.0966936)  # Calgary
df_new["Distance"] = df_new.apply(lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
                                  axis=1)
top_5_recommendations = get_recommendations_include_rating([category], df_new)
print("#####################################################################################")
pd.set_option('display.max_columns', None)
print(top_5_recommendations)
pd.reset_option('display.max_rows')
print("#####################################################################################")
