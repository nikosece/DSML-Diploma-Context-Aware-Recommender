import pandas as pd
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
        if keywords is not None:
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform(df['categories'])
            tfidf_keywords = tfidf.transform(keywords)
            cosine_sim1 = linear_kernel(tfidf_matrix, tfidf_keywords)
            sim_scores1 = list(enumerate(cosine_sim1))
            sim_scores1 = sorted(sim_scores1, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores1
            # sim_scores1 = sim_scores1[0][0]
            # a = [df.iloc[sim_scores1].categories.__str__()]
            # tfidf_res = tfidf.transform(a)
            # cosine_sim = linear_kernel(tfidf_matrix, tfidf_res)
            # sim_scores = list(enumerate(cosine_sim))
            # sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[0:50]
            new_df = df.iloc[[ids[0] for ids in sim_scores]]
            moderate = new_df.review_count.describe()[4]
            max_di = new_df.distance.max()
            min_di = new_df.distance.min()
        else:
            sim_scores = list(enumerate(df.score))
            moderate = df.review_count.describe()[4]
            max_di = df.distance.max()
            min_di = df.distance.min()
        score_dict = {}

        for ids in sim_scores:
            index = df.iloc[[ids[0]]].index[0]
            rating = df.iloc[[ids[0]]].stars.values[0]
            distance = df.iloc[[ids[0]]].distance.values[0]
            rating_count = df.iloc[[ids[0]]].review_count.values[0]
            if keywords is not None:
                fm_score = ids[1][0]
            else:
                fm_score = df.iloc[[ids[0]]].score.values[0]
            rating_contribution = RatingExtractor.get_rating_weight_with_quantity(rating, rating_count, moderate)
            if max_di == min_di:
                normalized_di = 1
            else:
                normalized_di = (max_di - distance) / (max_di - min_di)
            final_score = RecommenderEngine.calculate_final_score(fm_score, rating_contribution, normalized_di, vechile)
            score_dict[index] = final_score

        # sort cities by score and index.
        sorted_scores = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)

        counter = 0
        # create an empty results data frame.
        resulted = pd.DataFrame(columns=('name', 'city', 'categories', 'stars', 'score', 'distance',
                                         'latitude', 'longitude', 'duration'))

        # get highest scored 10 businesses.
        for i in sorted_scores:
            resulted = resulted.append({'name': df.loc[i[0]]['name'], 'city': df.loc[i[0]]['city'],
                                        'categories': df.loc[i[0]]['categories'], 'stars': df.loc[i[0]]['stars'],
                                        'distance': df.loc[i[0]]['distance'],
                                        'score': i[1], 'duration': df.loc[i[0]]['duration'],
                                        'latitude': df.loc[i[0]]['latitude'],
                                        'longitude': df.loc[i[0]]['longitude']
                                        },
                                       ignore_index=True)
            counter += 1

            if counter >= 10:
                break

        return resulted
