from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .forms import CityForm
import pandas as pd
import numpy as np

df_b = pd.read_csv('/home/anonymous/Documents/Diploma-Recommender/Recommendation/rec/Dataset/bussines_R_attributes.csv',
                   dtype={'name': str,
                          'city': str, 'state': str,
                          'latitude': float, 'longitude': float,
                          'business_id': str, 'stars': np.float32,
                          'categories': str,
                          'review_count': np.int32,
                          'RestaurantsPriceRange2': np.float16,
                          'valet': np.float16,
                          'street': np.float16,
                          'validated': np.float16, 'lot': np.float16,
                          'garage': np.float16,
                          'RestaurantsTakeOut': np.float16,
                          'GoodForKids': np.float16,
                          'Caters': np.float16,
                          'RestaurantsReservations': np.float16,
                          'BikeParking': np.float16,
                          'RestaurantsDelivery': np.float16,
                          'classy': np.float16, 'romantic': np.float16,
                          'divey': np.float16, 'hipster': np.float16,
                          'upscale': np.float16, 'trendy': np.float16,
                          'touristy': np.float16,
                          'intimate': np.float16, 'casual': np.float16,
                          'HasTV': np.float16, 'NoiseLevel': np.float16,
                          'BusinessAcceptsCreditCards': np.float16,
                          'RestaurantsGoodForGroups': np.float16,
                          'latenight': np.float16, 'dessert': np.float16,
                          'lunch': np.float16, 'dinner': np.float16,
                          'brunch': np.float16, 'breakfast': np.float16,
                          'OutdoorSeating': np.float16, 'WiFi': str,
                          'RestaurantsAttire': str
                          }, index_col='business_id')

city = df_b.city.value_counts()
city_list = list(city.index)
# a = dict(zip(df_b.city, df_b.state))
# my_dict = dict()
# for v in list(a.values()):
#     my_dict[v] = set()
# for  in list(my_dict.keys()):
#     my_dict[i] = my_dict[i]
tuple_list = tuple()
for i in range(len(city_list)):
    # tuple_list = tuple_list + ((a[city_list[i]], (i, city_list[i],),),)
    tuple_list = tuple_list + ((i, city_list[i]),)


# Create your views here.

def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # check whether it's valid:
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            choice = int(request.POST["City"])
            print(tuple_list[choice][1])
        else:
            print("not Valid")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CityForm(City=tuple_list)
    return render(request, 'rec/index.html', {'form': form})
