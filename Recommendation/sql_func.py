from rec.models import Business


class Sqlfunctions:
    def __init__(self):
        print("Functions initialized")

    @staticmethod
    def state_city_group():
        grouped = Business.objects.values('state__name', 'city__name').distinct()
        g = {}
        for row in grouped:
            if row['state__name'] in g:
                g[row['state__name']].append(row['city__name'])
            else:
                g[row['state__name']] = [row['city__name']]
        for key in list(g.keys()):
            g[key].sort()
        tuple_list = (('', ''),)
        for k, v in g.items():
            tuple2 = tuple()
            for city in v:
                tuple2 = tuple2 + ((city, city),)  # (number of city, city name)
            tuple_list = tuple_list + ((k, tuple2,),)  # grouped by state
        return tuple_list
