import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from rating_extractor import RatingExtractor
import operator
import json


class RecommenderEngine:
    def __init__(self):
        print("engine initialized")

    @staticmethod
    def calculate_final_score(cs, r):
        """ Combine relevance and weighted review stars
        weight for cs is 0.7 and for r is 0.3
        :param cs: relevance score between 0 and 1
        :param r: review stars between 0 and 5
        :return: Returns value between 0 and 100"""
        cs_normalize = cs * 100
        r_normalize = 100 * r / 5
        amount = cs_normalize * 0.7 + r_normalize * 0.3
        return amount

    # Version-2
    @staticmethod
    def get_recommendations_include_rating(keywords, df):
        """Based on user's keywords find the most relevant
        business. Then based on that look for similar businesses.
        After that, recalculate the score based on review and
        the total number of reviews. At the end the top five
        are returned."""
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['categories'])
        tfidf_keywords = tfidf.transform(keywords)
        cosine_sim1 = linear_kernel(tfidf_matrix, tfidf_keywords)
        sim_scores1 = list(enumerate(cosine_sim1))
        sim_scores1 = sorted(sim_scores1, key=lambda x: x[1], reverse=True)
        sim_scores1 = sim_scores1[0][0]
        a = [df.iloc[sim_scores1].categories.__str__()]
        tfidf_res = tfidf.transform(a)
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_res)
        sim_scores = list(enumerate(cosine_sim))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[0:50]

        score_dict = {}

        for ids in sim_scores:
            index = df.iloc[[ids[0]]].index[0]
            rating = df.iloc[[ids[0]]].stars.values[0]
            rating_count = df.iloc[[ids[0]]].review_count.values[0]
            threshold = 1000
            rating_contribution = RatingExtractor.get_rating_weight_with_quantity(rating, rating_count, 50)
            final_score = RecommenderEngine.calculate_final_score(ids[1][0], rating_contribution)
            score_dict[index] = final_score

        # sort cities by score and index.
        sorted_scores = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)

        counter = 0

        # create an empty results data frame.
        resulted = pd.DataFrame(columns=('id', 'Name', 'city', 'category', 'stars', 'score'))

        # get highest scored 5 cities.
        for i in sorted_scores:
            # print index and score of the city.
            # print(i[0], i[1])
            resulted = resulted.append({'id': i[0], 'Name': df.loc[i[0]]['name'], 'city': df.loc[i[0]]['city'],
                                        'category': df.loc[i[0]]['categories'], 'stars': df.loc[i[0]]['stars'],
                                        'score': i[1]}, ignore_index=True)
            counter += 1

            if counter > 4:
                break

        # convert DF to json.
        # json_result = json.dumps(resulted.to_dict('records'))
        return resulted
