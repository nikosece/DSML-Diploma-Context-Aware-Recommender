import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from rating_extractor import RatingExtractor
import operator


class RecommenderEngine:
    def __init__(self):
        print("engine initialized")

    @staticmethod
    def calculate_final_score(cs, r, distance, vechile):
        """ Combine relevance and weighted review stars
        weight for cs is 0.45 for r is 0.45 and for
        distance is 0.1
        :param vechile: type of transport
        :param distance: Distance from user's location
        :param cs: relevance score between 0 and 1
        :param r: review stars between 0 and 5
        :return: Returns value between 0 and 100"""
        cs_normalize = cs * 100
        r_normalize = 100 * (r - 0.5) / 4.5     # (r-min_r)/(max_r - min_r)
        if vechile == 0:
            amount = r_normalize * 0.75 + distance * 100 * 0.25
        else:
            amount = r_normalize * 0.4 + distance * 100 * 0.6
        return amount

    # Version-2
    @staticmethod
    def get_recommendations_include_rating(df, vechile, keywords=None):
        """Based on user's keywords find the most relevant
        business. Then based on that look for similar businesses.
        After that, recalculate the score based on review and
        the total number of reviews. Also normalized distance
        is used in the final score.
        At the end the top five
        are returned."""
        # At this point category filtering is completed in two steps
        # 1) Find the most similar business with keyword
        # 2) Find the most similar businesses withe the above business
        # I may use only step1, it seems more accurate
        moderate = np.percentile(np.array([i.review_count for i in df]), 25)
        max_di = max([i.distance for i in df])
        min_di = min([i.distance for i in df])

        for i in df:
            rating = float(i.stars)
            distance = i.distance
            rating_count = i.review_count
            fm_score = i.score
            rating_contribution = RatingExtractor.get_rating_weight_with_quantity(rating, rating_count, moderate)
            if max_di == min_di:
                normalized_di = 1
            else:
                normalized_di = (max_di - distance) / (max_di - min_di)
            final_score = RecommenderEngine.calculate_final_score(fm_score, rating_contribution, normalized_di, vechile)
            i.score = final_score

        # sort cities by score and index.
        top_items = sorted(df, key=lambda x: x.score, reverse=True)
        top_items = top_items[0:10]

        # create an empty results data frame.
        resulted = pd.DataFrame(columns=('name', 'city', 'categories', 'stars', 'score', 'distance',
                                         'latitude', 'longitude', 'duration'))

        # get highest scored 10 businesses.
        for i in top_items:
            cat = " ,".join([j.name for j in i.categories.all()])
            resulted = resulted.append({'name': i.name, 'city': i.city.name,
                                        'categories': cat, 'stars': i.stars,
                                        'distance': i.distance,
                                        'score': i.score, 'duration': i.duration,
                                        'latitude': i.latitude,
                                        'longitude': i.longtitude
                                        },
                                       ignore_index=True)

        return resulted
