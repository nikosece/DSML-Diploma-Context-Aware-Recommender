from recommender_engine import RecommenderEngine
import pandas as pd


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

# Version 2 requests are below:
print("#################")
top_5_recommendations = get_recommendations_include_rating(["Bars"], df_b)
pd.set_option('display.max_columns', None)
print(top_5_recommendations)
pd.reset_option('display.max_rows')
print("#################")
