from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .forms import CityForm, CategoryForm
from recommender_engine import RecommenderEngine
from functions import Functions
from create_map import Create_map
import os.path
from os import path


def create_categories_form():
    global selected_city, df_new, df_explode, categories, to_show, form2
    df_new = Functions.filtering_city(df_b, selected_city)
    df_explode = df_new.assign(categories=df_new.categories.str.split(', ')).explode('categories')
    categories = df_explode.categories.value_counts()
    categories = categories.to_frame()
    categories = categories[categories.categories <= categories.categories.describe()[5]]
    to_delete = list(categories.index)
    df_new = Functions.remove_categories(df_new, "Restaurants")
    df_new = Functions.remove_categories(df_new, "Food")
    for d in reversed(to_delete):
        df_new = Functions.remove_categories(df_new, d)
    df_explode = df_new.assign(categories=df_new.categories.str.split(', ')).explode('categories')
    categories = df_explode.categories.value_counts()
    to_show = [categories.index[c] for c in range(0, categories.shape[0])]
    category_tuple = (('', '----'),)
    for j in range(len(to_show)):
        category_tuple = category_tuple + ((j, to_show[j]),)
    form2 = CategoryForm(Category=category_tuple)


def index(request):
    global selected_city, df_new, df_explode, categories, to_show, form2, cols, row_list, top_10_recommendations, origin
    # This request happens each time the user selects a city from the dropdown list
    if request.method == 'POST' and "City" in request.POST:
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            selected_city = city_dict[int(request.POST["City"])]
            create_categories_form()
    # This request happens each time the user submits categories from the dropdown list
    elif request.method == 'POST' and "Category" in request.POST:
        selected_category = request.POST.getlist('Category')
        selected_category = [to_show[int(s)] for s in selected_category]
        selected_category = ", ".join(selected_category)  # Combine all selected categories into one string
        origin = (df_new.iloc[0].latitude, df_new.iloc[0].longitude)

        df_new["Distance"] = df_new.apply(
            lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
            axis=1)
        top_10_recommendations = RecommenderEngine.get_recommendations_include_rating([selected_category], df_new)
        # Create_map.plot(top_10_recommendations, selected_city, origin, True)
        cols = ["Name", "Category", "Stars", "Distance", "Score"]
        name_list = top_10_recommendations.name.to_list()
        cat_list = top_10_recommendations.category.to_list()
        star_list = top_10_recommendations.stars.to_list()
        distance_list = top_10_recommendations.distance.to_list()
        distance_list = ["{:.2f}".format(a) for a in distance_list]
        score_list = top_10_recommendations.score.to_list()
        score_list = ["{:.2f} %".format(a) for a in score_list]
        row_list = []
        for m in range(len(name_list)):
            row_list.append({"name": name_list[m], "category": cat_list[m], "stars": star_list[m],
                             "distance": distance_list[m], "score": score_list[m]})
        return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CityForm(City=tuple_list)
        selected_city = city_dict[0]
        create_categories_form()
    return render(request, 'rec/index.html', {'form': form, 'form2': form2})


def results(request):
    return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})


def show_map(request):
    map_path = 'rec/' + selected_city + '.html'
    if not path.exists(
            "/home/anonymous/Documents/Diploma-Recommender/Recommendation/rec/templates/rec/" + selected_city +
            '.html'):
        Create_map.plot(top_10_recommendations, selected_city, origin, True)
    return render(request, map_path)


df_b = Functions.read_business()
grouped = {k: set(v) for k, v in df_b.groupby('state')['city']}  # group by cities by state
grouped = {k: list(v) for k, v in grouped.items()}
tuple_list = (('', '----'),)
i = 0  # i keeps city number
city_dict = dict()
# Create the tuple needed for city choices in django form
for k, v in grouped.items():
    tuple2 = tuple()
    for city in v:
        tuple2 = tuple2 + ((i, city),)  # (number of city, city name)
        city_dict[i] = city
        i = i + 1
    tuple_list = tuple_list + ((k, tuple2,),)  # grouped by state

df_new = df_explode = categories = to_show = form2 = cols = row_list = top_10_recommendations = origin = None
selected_city = city_dict[0]  # Choose the first available city to initialize index forms
create_categories_form()
