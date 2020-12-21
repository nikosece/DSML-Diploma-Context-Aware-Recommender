from math import e


class RatingExtractor:
    def __init__(self):
        print("rating initialized")

    @staticmethod
    def get_rating_weight_with_quantity(rating, c, t, q=10):
        """

        :param rating: indicates the rating for the destination
        :param c: rating count
        :param t: indicates the amount of rating as a threshold where score will be halved.
        :param q: indicates the percentage of rating for general score. (default is 10.)
        :return: Returns value between -q and q. for rating input between 0 and 10.
        """
        if rating > 10 or rating < 0:
            return None
        else:
            m = (2 * q) / 10  # 10 because rating varies between 0 and 10
            b = -q
            val = (m * rating) + b

            res = e ** ((-t * 0.68) / c)

            return val * res
