from recommender_engine import RecommenderEngine
import json
import pandas as pd


# def categorize(top=10, category=False):
#     """Select a specific category or sub-category to be involved
#     If category is True then user have to choose one,
#     else the top category is selected by default"""
#     df_explode = df_b.assign(categories=df_b.categories.str.split(', ')).explode('categories')["categories"]
#     print("There are the top {} categories".format(top))
#     print(df_explode.value_counts(normalize=True).nlargest(top))
#     if category:
#         a = input("Please specify category string")
#         print("{} selected".format(a))
#         df_b_specific = df_b[df_b['categories'].str.contains(a, na=False)]
#     else:
#         for val, cnt in df_explode.value_counts(normalize=True).nlargest(1).iteritems():
#             print("{} selected".format(val))
#             df_b_specific = df_b[df_b['categories'].str.contains(val, na=False)]
#     df_r_specific = df_r[df_r['business_id'].isin(df_b_specific.index)]
#     return df_b_specific, df_r_specific


def get_recommendations_include_rating(keywords, df):
    return RecommenderEngine.get_recommendations_include_rating(keywords, df)


def get_top_5_city_names_out_of_json(json_string):
    list_var = json.loads(json_string)
    result = []
    max_var = len(list_var)
    i = 0
    while i < max_var:
        result.append((list_var[i]['Name'], list_var[i]['score']))
        i += 1

    return result


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

# Version 2 requests are below:
print("#################")
top_5_cultural_with_rating = get_recommendations_include_rating(["Bars"], df_b)
# city_names_for_cultural_rating = get_top_5_city_names_out_of_json(top_5_cultural_with_rating)
pd.set_option('display.max_rows', len(top_5_cultural_with_rating))
print(top_5_cultural_with_rating)
pd.reset_option('display.max_rows')
# print(city_names_for_cultural_rating)
print("#################")
