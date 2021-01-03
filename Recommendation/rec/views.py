from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .forms import CityForm, CategoryForm
from recommender_engine import RecommenderEngine
from functions import Functions
from create_map import Create_map
import pandas as pd
import numpy as np

df_b = pd.read_csv('/home/anonymous/Documents/Diploma-Recommender/Recommendation/Dataset/bussines_R_attributes.csv',
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

# city = df_b.city.value_counts()
# city_list = list(city.index)
grouped = {k: set(v) for k, v in df_b.groupby('state')['city']}
grouped = {k: list(v) for k, v in grouped.items()}
tuple_list = tuple()
i = 0
city_dict = dict()
for k, v in grouped.items():
    tuple2 = tuple()
    for city in v:
        tuple2 = tuple2 + ((i, city),)
        city_dict[i] = city
        i = i + 1
    tuple_list = tuple_list + ((k, tuple2,),)

df_new = ""
df_explode = ""
categories = ""
to_show = ""
selected_city = ""


# Create your views here.

def index(request):
    global selected_city, df_new, df_explode, categories, to_show
    # if this is a POST request we need to process the form data
    if request.method == 'POST' and "City" in request.POST:
        # create a form instance and populate it with data from the request:
        # check whether it's valid:
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            city_choice = city_dict[int(request.POST["City"])]
            selected_city = city_choice
            df_new = Functions.filtering_city(df_b, city_choice)
            df_new = Functions.remove_categories(df_new, "Restaurants")
            df_new = Functions.remove_categories(df_new, "Food")
            df_explode = df_new.assign(categories=df_new.categories.str.split(', ')).explode('categories')
            categories = df_explode.categories.value_counts()
            max_va = 20
            if categories.shape[0] < 20:
                max_va = categories.shape[0]
            to_show = [categories.index[c] for c in range(0, max_va)]
            category_tuple = tuple()
            for j in range(len(to_show)):
                category_tuple = category_tuple + ((j, to_show[j]),)
            form2 = CategoryForm(Category=category_tuple)
    elif request.method == 'POST':
        selected_category = request.POST.getlist('Category')
        selected_category = [to_show[int(s)] for s in selected_category]
        selected_category = ", ".join(selected_category)
        categories = categories.to_frame()
        categories = categories[categories.categories <= categories.categories.describe()[5]]
        to_delete = list(categories.index)
        for d in reversed(to_delete):
            df_new = Functions.remove_categories(df_new, d)
        origin = (df_new.iloc[0].latitude, df_new.iloc[0].longitude)
        df_new = Functions.remove_categories(df_new, "Restaurants")
        df_new = Functions.remove_categories(df_new, "Food")

        df_new["Distance"] = df_new.apply(
            lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
            axis=1)
        top_10_recommendations = RecommenderEngine.get_recommendations_include_rating([selected_category], df_new)
        Create_map.plot(top_10_recommendations, selected_city, origin, True)
        print("#####################################################################################")
        pd.set_option('display.max_columns', None)
        print(top_10_recommendations.filter(["name", "category", "stars", "total_reviews", "distance", "score"]))
        pd.reset_option('display.max_rows')
        print("#####################################################################################")
        return render(request, 'rec/'+selected_city+'.html')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CityForm(City=tuple_list)
        form2 = CategoryForm(Category=())
    return render(request, 'rec/index.html', {'form': form, 'form2': form2})
