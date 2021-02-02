import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from rating_extractor import RatingExtractor


class RecommenderEngine:
    def __init__(self):
        print("engine initialized")

    @staticmethod
    def calculate_final_score(cs, r, count, distance, vechile):
        """ Combine relevance and weighted review stars
        weight for cs is 0.45 for r is 0.45 and for
        distance is 0.1
        :param count: normalized review count
        :param vechile: type of transport
        :param distance: Distance from user's location
        :param cs: relevance score between 0 and 1
        :param r: normalized rating value
        :return: Returns value between 0 and 100"""
        if vechile == 0:
            amount = cs * 0.15 + r * 0.25 + count * 0.6  # + distance * 100 * 0.2
        else:
            amount = cs * 0.15 + r * 0.1 + count * 0.35 + distance * 0.4
        return amount

    # Version-2
    @staticmethod
    def similarity_filter(df, k, keywords):
        tfidf = TfidfVectorizer(stop_words='english')
        categories = []
        for row in df:
            categories.append([c['name'] for c in row.categories.values()])
        categories = [", ".join(c) for c in categories]
        tfidf_matrix = tfidf.fit_transform(categories)
        tfidf_keywords = tfidf.transform(keywords)
        cosine_sim1 = linear_kernel(tfidf_matrix, tfidf_keywords)
        sim_scores = list(enumerate(cosine_sim1))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[0:k]
        new_df = [df[ids[0]] for ids in sim_scores if ids[1] > 0]
        for i in range(len(new_df)):
            new_df[i].score = sim_scores[i][1][0]
        return new_df

    @staticmethod
    def get_recommendations_include_rating(df, vechile):
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
        all_rates = [float(i.stars) for i in df]
        all_counts = [i.review_count for i in df]
        max_rate = max(all_rates)
        min_rate = min(all_rates)
        max_count = max(all_counts)
        min_count = min(all_counts)
        # moderate = np.percentile(np.array([i.review_count for i in df]), 25)
        max_di = max([i.distance for i in df])
        min_di = min([i.distance for i in df])

        for i in df:
            rating = float(i.stars)
            distance = i.distance
            rating_count = i.review_count
            fm_score = 100 * i.score
            normalized_rate = 100 * (rating - min_rate) / (max_rate - min_rate)
            normalized_count = 100 * (rating_count - min_count) / (max_count - min_count)
            # rating_contribution = RatingExtractor.get_rating_weight_with_quantity(rating, rating_count, moderate)
            if max_di == min_di:
                normalized_di = 100
            else:
                normalized_di = 100 * (max_di - distance) / (max_di - min_di)
            final_score = RecommenderEngine.calculate_final_score(fm_score, normalized_rate, normalized_count,
                                                                  normalized_di, vechile)
            i.score = final_score

        # sort cities by score and index.
        top_items = sorted(df, key=lambda x: x.score, reverse=True)
        top_items = top_items[0:50]

        # create an empty results data frame.
        resulted = pd.DataFrame(columns=('name', 'city', 'categories', 'stars', 'score', 'distance',
                                         'latitude', 'longitude', 'duration', 'id', 'r_count', 'address'))

        # get highest scored 50 businesses.
        for i in top_items:
            cat = " ,".join([j.name for j in i.categories.all()])
            resulted = resulted.append({'name': i.name, 'city': i.city.name,
                                        'categories': cat, 'stars': float(i.stars),
                                        'distance': i.distance,
                                        'score': i.score, 'duration': i.duration,
                                        'latitude': i.latitude,
                                        'longitude': i.longtitude, 'id': i.business_id,
                                        'r_count': i.review_count,
                                        'address': i.address
                                        },
                                       ignore_index=True)
        return resulted
