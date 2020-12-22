from functions import Functions
from context_create import Context_create
import pandas as pd
import numpy as np

df_b = pd.read_csv('bussines_R.csv', dtype={'name': str,
                                            'city': str, 'state': str, 'postal_code': str,
                                            'latitude': float, 'longitude': float,
                                            'business_id': str, 'stars': float,
                                            'attributes': str, 'categories': str}, index_col='business_id')

df_c = pd.read_csv("checkin_R.csv", dtype={'weekday': np.int8, 'season': np.int8,
                                           'session': str}, parse_dates=["date"], index_col='business_id')

df_b = Functions.remove_categories(df_b)

df = Context_create.session_context(df_b, df_c, 20)
