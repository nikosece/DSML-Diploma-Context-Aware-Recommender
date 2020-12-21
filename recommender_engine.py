import pandas as pd
from cosine_similarity import CosineSimilarity
from rating_extractor import RatingExtractor
import operator
import json


class RecommenderEngine:
    def __init__(self):
        print("engine initialized")

    @staticmethod
    def calculate_final_score(cs, r):
        amount = (cs / 100) * r
        return cs + amount

    # Version-2
    @staticmethod
    def get_recommendations_include_rating(keywords, df, bus):

        score_dict = {}

        for index, row in df.iterrows():
            try:
                cs_score = CosineSimilarity.cosine_similarity_of(row['text'], keywords)
                if cs_score > 0:
                    if row['business_id'] not in score_dict:
                        score_dict[row['business_id']] = cs_score
                    else:
                        score_dict[row['business_id']] = (score_dict[row['business_id']] + cs_score) / 2.0
            except:
                continue
        for ids in list(score_dict.keys()):
            rating = bus.loc[[ids]].stars.values[0]
            rating_count = bus.loc[[ids]].review_count.values[0]
            threshold = 1000
            rating_contribution = RatingExtractor.get_rating_weight_with_quantity(rating, rating_count, threshold, 50)
            final_score = RecommenderEngine.calculate_final_score(score_dict[ids], rating_contribution)
            score_dict[ids] = final_score

        # sort cities by score and index.
        sorted_scores = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)

        counter = 0

        # create an empty results data frame.
        resulted = pd.DataFrame(columns=('Name', 'city', 'id', 'score'))

        # get highest scored 5 cities.
        for i in sorted_scores:
            # print index and score of the city.
            # print(i[0], i[1])
            resulted = resulted.append({'Name': bus.loc[i[0]]['name'], 'city': bus.loc[i[0]]['city'],
                                        'id': i, 'score': i[1]}, ignore_index=True)
            counter += 1

            if counter > 4:
                break

        # convert DF to json.
        json_result = json.dumps(resulted.to_dict('records'))
        return json_result
