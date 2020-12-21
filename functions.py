from geopy.distance import geodesic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class Functions:
    def __init__(self):
        print("Functions initialized")

    @staticmethod
    def filtering_city(df, city):
        new_df = df[(df.city == city)]
        return new_df

    @staticmethod
    def filtering_state(df, state):
        new_df = df[(df.state == state)]
        return new_df

    @staticmethod
    def filtering_stars(df, star):
        new_df = df[(df.stars >= star)]
        return new_df

    @staticmethod
    def calculate_distance(origin, dist):
        # (latitude, longitude) don't confuse
        return geodesic(origin, dist).kilometers

    @staticmethod
    def category_similarity(df, keyword):
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['categories'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)  # this compares all
        tfidf_keywords = tfidf.transform(keyword)
        cosine_sim1 = linear_kernel(tfidf_matrix, tfidf_keywords)
        sim_scores = list(enumerate(cosine_sim1))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_result = list(enumerate(cosine_sim[sim_scores[0][0]]))
        sim_result = sorted(sim_result, key=lambda x: x[1], reverse=True)
        sim_result = sim_result[0:16]
        sim_scores = sim_scores[0:16]
        #return sim_result
        for i in sim_scores:
            print(df.iloc[[i[0]]].categories.values)
