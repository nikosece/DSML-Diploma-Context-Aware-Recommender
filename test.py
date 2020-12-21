import pandas as pd
import numpy as np

df_r = pd.read_csv("reviews_R_context.csv", dtype={'user_id': str,
                                                   'user_id': str, 'review_stars': np.int8, 'text': str,
                                                   'weekday': np.int8, 'season': np.int8,
                                                   'session': str}, parse_dates=["date"], index_col='business_id')

# b = [0, 4, 8, 12, 16, 20, 24]
# l = ['Late Night', 'Early Morning', 'Morning', 'Noon', 'Eve', 'Night']
# df_c['session'] = pd.cut(df_c['hour'], bins=b, labels=l, include_lowest=True)
df_b = pd.read_csv('bussines_R.csv', dtype={'name': str,
                                            'city': str, 'state': str, 'postal_code': str,
                                            'latitude': float, 'longitude': float,
                                            'business_id': str, 'stars': float,
                                            'attributes': str, 'categories': str}, index_col='business_id')
df_c = pd.read_csv("checkin_R.csv", dtype={'weekday': np.int8, 'season': np.int8,
                                           'session': str}, parse_dates=["date"], index_col='business_id')

df_session = pd.read_csv("checkin_sessions.csv", dtype={'Early Morning': float, 'Eve': float,
                                                        'Late Night': float, 'Morning': float,
                                                        'Noon': float, 'total': float,
                                                        'Night': float}, index_col='business_id')

df_season = pd.read_csv("checkin_Season.csv", dtype={'Fall': float, 'Spring': float,
                                                     'Summer': float, 'Winter': float,
                                                     'total': float}, index_col='business_id')

df_weekday = pd.read_csv("checkin_Season.csv", dtype={'Friday': float,
                                                      'Monday': float,
                                                      'Saturday': float,
                                                      'Sunday': float,
                                                      'Thursday': float,
                                                      'Tuesday': float,
                                                      'Wednesday': float}, index_col='business_id')

#df_explode = df_b.assign(categories=df_b.categories.str.split(', ')).explode('categories')
#a = df_explode.categories.value_counts()
#categories = set(df_explode.categories.values.tolist())
#cities = set(df_b.city.values.tolist())
#states = set(df_b.state.values.tolist())


# Restaurants and Food is almost in any category, and that is not helpful so i will remove it
# phonix["categories"] = phonix.categories.str.replace("Restaurants, ","")
# phonix["categories"] = phonix.categories.str.replace("Food,","")
# origin = (33.60282,-111.98353)
# phonix["distance"] = phonix.apply(lambda row : Functions.calculate_distance(origin,(row['latitude'],row['longitude'])), axis = 0)
