import pandas as pd


def compute_sum(count):
    a = list(count.columns)
    count["total"] = count.sum(axis=1)
    for i in a:
        count[i] = count[i] / count["total"]

    for i in a:
        count[i] = 100 * count[i]
    return count


class Context_create:
    def __init__(self):
        print("Context create initialized")

    @staticmethod
    def weekdays(df):
        df = df.sort_index()
        maping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        df["Weekday"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Weekday'].value_counts().unstack().fillna(0)
        count = compute_sum(count)
        count.to_csv("review_weekdays.csv")

    @staticmethod
    def season(df):
        maping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        df["Season"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Season'].value_counts().unstack().fillna(0)
        count = compute_sum(count)

        count.to_csv("review_Season.csv")

    @staticmethod
    def session(df):
        count = df.groupby(df.index)['session'].value_counts().unstack().fillna(0)
        count = compute_sum(count)
        count.to_csv("review_sessions.csv")

    @staticmethod
    def session_context(df_b, df_c):
        df_b = df_b.filter(["categories"])
        df_c = df_c.filter(["session"])
        df = pd.merge(df_b, df_c, on='business_id', how='inner')
        df["categories"] = df.categories.str.replace("Restaurants, ", "")
        df["categories"] = df.categories.str.replace("Restaurants", "")
        df_explode = df.assign(categories=df.categories.str.split(', ')).explode('categories')