import pandas as pd
import matplotlib.pyplot as plt
import operator
from functions import plot_pie


def compute_sum(count):
    a = list(count.columns)
    count["total"] = count.sum(axis=1)
    for i in a:
        count[i] = count[i] / count["total"]

    for i in a:
        count[i] = 100 * count[i]
    return count


def extract(target, df_explode):
    return df_explode.groupby(df_explode.categories)[target].value_counts().unstack().fillna(0)


def plot(cols, count):
    top = 20
    fig, ax = plt.subplots(figsize=(11, 6), dpi=100, subplot_kw=dict(aspect="equal"))
    for col in cols:
        print("Plotting {} subplot".format(col))
        data = count[col].to_dict()
        sorted_data = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        sorted_data = sorted_data[0:top]
        plot_pie(sorted_data, ax)
        ax.set_title("Top {} categories for {}.".format(top, col),
                     fontdict={'fontsize': 20, 'fontweight': 'medium'})
        plt.savefig('/home/anonymous/Documents/Diploma-Recommender/Plots/context_plots/' + col + '.png', dpi='figure')
        plt.cla()


class Context_create:
    def __init__(self):
        print("Context create initialized")

    @staticmethod
    def weekdays(df, name):
        df = df.sort_index()
        maping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        df["Weekday"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Weekday'].value_counts().unstack().fillna(0)
        count = compute_sum(count)
        count.to_csv(name+"_weekdays.csv")

    @staticmethod
    def season(df, name):
        maping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        df["Season"] = df.season.map(maping)
        count = df.groupby(df.index)['Season'].value_counts().unstack().fillna(0)
        count = compute_sum(count)

        count.to_csv(name+"_Season.csv")

    @staticmethod
    def session(df, name):
        count = df.groupby(df.index)['session'].value_counts().unstack().fillna(0)
        count = compute_sum(count)
        count.to_csv(name+"_sessions.csv")

    @staticmethod
    def session_context(df_b, df_c):
        """ At this point the code creates plots
        for the seasons of the years, but with 2 or 3
        changes it creates for weekdays and sessions 
        of the day """
        df_b = df_b.filter(["categories"])
        maping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        df_c["season"] = df_c.season.map(maping)
        maping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        df_c["weekday"] = df_c.weekday.map(maping)
        df_c = df_c.filter(["season", "session", "weekday"])
        df = pd.merge(df_b, df_c, on='business_id', how='inner')
        df_explode = df.assign(categories=df.categories.str.split(', ')).explode('categories')
        for target in ["season", "session", "weekday"]:
            print("Creation of {} plots has been started".format(target))
            count = extract(target, df_explode)
            cols = list(count.columns)
            plot(cols, count)
