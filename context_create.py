import pandas as pd
import matplotlib.pyplot as plt
import operator


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
    def session_context(df_b, df_c, top=20):
        df_b = df_b.filter(["categories"])
        df_c = df_c.filter(["session"])
        df = pd.merge(df_b, df_c, on='business_id', how='inner')
        df_explode = df.assign(categories=df.categories.str.split(', ')).explode('categories')
        count = df_explode.groupby(df_explode.categories)['session'].value_counts().unstack().fillna(0)
        sessions = list(count.columns)
        fig, ax = plt.subplots(figsize=(80, 60), dpi=250, subplot_kw=dict(aspect="equal"))
        for session in sessions:
            data = count[session].to_dict()
            sorted_data = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
            sorted_data = sorted_data[0:top]
            values = [x[1] for x in sorted_data]
            wedges, texts = ax.pie(values, textprops=dict(color="w"))
            ingredients = [x[0] for x in sorted_data]
            ax.legend(wedges, ingredients,
                      title="Categories",
                      loc="center left",
                      title_fontsize=80,
                      bbox_to_anchor=(1, 0, 0.5, 1),
                      prop={'size': 60})
            if session == "Morning":
                a = "in " + session
            else:
                a = "at " + session
            ax.set_title("Preference {} for top {} categories".format(a, top),
                         fontdict={'fontsize': 90, 'fontweight': 'medium'})
            plt.savefig(session+'.png', dpi='figure')
            plt.cla()
        # a = list(count.columns)
        # for i in a:
        #     print(count[i].describe().filter(["25%", "50%", "75%"]))
        # return count
