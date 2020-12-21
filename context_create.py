class Context_create:
    def __init__(self):
        print("Context create initialized")

    @staticmethod
    def weekdays(df):
        df = df.sort_index()
        maping = {}
        maping[0] = "Monday"
        maping[1] = "Tuesday"
        maping[2] = "Wednesday"
        maping[3] = "Thursday"
        maping[4] = "Friday"
        maping[5] = "Saturday "
        maping[5] = "Saturday"
        maping[6] = "Sunday"
        df["Weekday"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Weekday'].value_counts().unstack().fillna(0)
        a = list(count.columns)
        count["total"] = count.sum(axis=1)
        for i in a:
            count[i] = count[i ] /count["total"]

        for i in a:
            count[i] = 100 *count[i]

        count.to_csv("review_weekdays.csv")

    @staticmethod
    def season(df):
        maping = {}
        maping[1] = "Spring"
        maping[2] = "Summer"
        maping[3] = "Fall"
        maping[4] = "Winter"
        df["Season"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Season'].value_counts().unstack().fillna(0)
        a = list(count.columns)
        count["total"] = count.sum(axis=1)
        for i in a:
            count[i] = count[i ] /count["total"]

        for i in a:
            count[i] = 100 *count[i]

        count.to_csv("review_Season.csv")

    @staticmethod
    def session(df):
        count = df.groupby(df.index)['session'].value_counts().unstack().fillna(0)
        a = list(count.columns)
        count["total"] = count.sum(axis=1)
        for i in a:
            count[i] = count[i ] /count["total"]

        for i in a:
            count[i] = 100 *count[i]

        count.to_csv("review_sessions.csv")
