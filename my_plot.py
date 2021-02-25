import matplotlib.pyplot as plt
import pickle
from matplotlib.patches import Rectangle
import numpy as np


def plot_hist(data, titles, name, bins=10):
    # Generate random data
    # Colours for different percentiles
    perc_25_colour = 'gold'
    perc_50_colour = 'mediumaquamarine'
    perc_75_colour = 'deepskyblue'
    perc_95_colour = 'peachpuff'

    # Plot the Histogram from the random data
    fig, ax = plt.subplots(figsize=(12, 8), dpi=400)

    '''
    counts  = numpy.ndarray of count of data ponts for each bin/column in the histogram
    bins    = numpy.ndarray of bin edge/range values
    patches = a list of Patch objects.
            each Patch object contains a Rectnagle object. 
            e.g. Rectangle(xy=(-2.51953, 0), width=0.501013, height=3, angle=0)
    '''
    counts, bins, patches = ax.hist(data, facecolor=perc_50_colour, edgecolor='gray', bins=bins)

    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins.round(2))
    plt.xticks(rotation=70)

    # Set the graph title and axes titles
    plt.title(titles, fontsize=20)
    plt.ylabel('Count', fontsize=15)
    plt.xlabel('Number of reviews', fontsize=15)

    # Change the colors of bars at the edges
    twentyfifth, seventyfifth, ninetyfifth = np.percentile(data, [25, 75, 95])
    for patch, leftside, rightside in zip(patches, bins[:-1], bins[1:]):
        if rightside < twentyfifth:
            patch.set_facecolor(perc_25_colour)
        elif leftside > ninetyfifth:
            patch.set_facecolor(perc_95_colour)
        elif leftside > seventyfifth:
            patch.set_facecolor(perc_75_colour)

    # Calculate bar centre to display the count of data points and %
    bin_x_centers = 0.5 * np.diff(bins) + bins[:-1]
    bin_y_centers = ax.get_yticks()[1] * 0.25

    # Display the the count of data points and % for each bar in histogram
    for i in range(len(bins) - 1):
        bin_label = "{0:,}".format(counts[i]) + "  ({0:,.2f}%)".format((counts[i] / counts.sum()) * 100)
        plt.text(bin_x_centers[i], bin_y_centers, bin_label, rotation=90, rotation_mode='anchor')

    # Annotation for bar values
    ax.annotate('Each bar shows count and percentage of total',
                xy=(.85, .30), xycoords='figure fraction',
                horizontalalignment='center', verticalalignment='bottom',
                fontsize=10, bbox=dict(boxstyle="round", fc="white"),
                rotation=-90)

    # create legend
    handles = [Rectangle((0, 0), 1, 1, color=c, ec="k") for c in
               [perc_25_colour, perc_50_colour, perc_75_colour, perc_95_colour]]
    labels = ["0-25 Percentile", "25-50 Percentile", "50-75 Percentile", ">95 Percentile"]
    plt.legend(handles, labels, bbox_to_anchor=(0.5, 0., 0.80, 0.99))

    # Display the graph
    # plt.show()
    fig.savefig(name + '.jpeg', dpi=400, bbox_inches='tight')


df_r = pickle.load(open('/home/anonymous/Documents/Diploma-Recommender/df_r.pickle', "rb"))
df_u = pickle.load(open('/home/anonymous/Documents/Diploma-Recommender/df_u.pickle', "rb"))
df_b = pickle.load(open('/home/anonymous/Documents/Diploma-Recommender/df_b.pickle', "rb"))
data = df_b['count'].values
titles = 'Distribution of total number of reviews for each business'
plot_hist(data, titles, 'business')
data = df_u['count'].values
titles = 'Distribution of total number of reviews for each user'
plot_hist(data, titles, 'users')
