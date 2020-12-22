from geopy.distance import geodesic


class Functions:
    def __init__(self):
        print("Functions initialized")

    @staticmethod
    def filtering_city(df, city):
        new_df = df[(df.city == city)]
        return new_df

    @staticmethod
    def filtering_state(df, state):
        new_df = df[(df.state == state)]
        return new_df

    @staticmethod
    def filtering_stars(df, star):
        new_df = df[(df.stars >= star)]
        return new_df

    @staticmethod
    def calculate_distance(origin, dist):
        # (latitude, longitude) don't confuse
        return geodesic(origin, dist).kilometers

    @staticmethod
    def remove_categories(df):
        """As food and Restaurants not specify important information
        when they are combined with other categories, the are removed
        for better classification"""
        df.categories.replace('(^Food, |, Food$)', '', regex=True, inplace=True)
        df.categories.replace(', Food,', ',', regex=True, inplace=True)
        df.categories.replace('(^Restaurants, |, Restaurants$)', '', regex=True, inplace=True)
        df.categories.replace(', Restaurants,', ',', regex=True, inplace=True)
        return df
