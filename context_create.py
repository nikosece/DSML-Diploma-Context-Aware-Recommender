import pandas as pd
import matplotlib.pyplot as plt
import operator
from functions import plot_pie


def compute_sum(df):
    """df contains how many times a specific
    context was seen and total is the sum of them"""
    # a = list(df.columns)
    df["total"] = int(df.sum(axis=1))
    # Use this only if you want percentage values
    # for i in a:
    #     df[i] = 100 * df[i] / df["total"]
    return df


def extract(target, df_explode):
    """" Group by categories and count values
    for each context variable"""
    return df_explode.groupby(df_explode.categories)[target].value_counts().unstack().fillna(0)


def plot(cols, count):
    """Plot pie diagrams for each context"""
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
        """Group by business_id and
        save weekdays context variable"""
        df = df.sort_index()
        maping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
        df["Weekday"] = df.weekday.map(maping)
        count = df.groupby(df.index)['Weekday'].value_counts().unstack().fillna(0)
        count = count.astype(int)
        count = compute_sum(count)
        count.to_csv(name + "_weekdays.csv")

    @staticmethod
    def season(df, name):
        """Group by business_id and
                save season context variable"""
        maping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        df["Season"] = df.season.map(maping)
        count = df.groupby(df.index)['Season'].value_counts().unstack().fillna(0)
        count = compute_sum(count)

        count.to_csv(name + "_Season.csv")

    @staticmethod
    def session(df, name):
        """Group by business_id and
                        save session context variable"""
        count = df.groupby(df.index)['session'].value_counts().unstack().fillna(0)
        count = compute_sum(count)
        count.to_csv(name + "_sessions.csv")

    @staticmethod
    def session_context(df_b, df_c):
        """ At this point the code creates pie plots
        for all of the three context variables"""
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
