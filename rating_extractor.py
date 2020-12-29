from math import e
import numpy as np


class RatingExtractor:
    def __init__(self):
        print("rating initialized")

    @staticmethod
    def get_rating_weight_with_quantity(rating, quantity, moderate=30):
        """
        :param rating: indicates the rating for the destination
        :param quantity: rating count
        :param moderate: indicates the amount of rating as a threshold where score will be halved.
                30 is default as median value
        :return: Returns value between 0 and 5 for rating input between 0 and 5.
        """
        if rating > 5 or rating < 0:
            return None
        else:
            a = -moderate / np.log(0.5)
            rating = rating / 2
            res = rating * (1 - e ** (-quantity / a))
            return rating + res
