from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .forms import CityForm, CategoryForm, ChoiceForm, VechileForm
from recommender_engine import RecommenderEngine
from functions import Functions
from create_map import Create_map
import numpy as np
import math
import pickle
from scipy import sparse
import pathlib


def save_pickle(var, name):
    with open(name + '.pickle', 'wb') as fle:
        pickle.dump(var, fle, protocol=pickle.HIGHEST_PROTOCOL)


def model_predict(df, k=50, tags=None, user_id=None):
    if user_id is None:
        user_feature_map = dataset.mapping()[1]
        user_id = 0
        user_feature_list = tags
        num_features = len(user_feature_list)
        normalised_val = 1.0 / num_features
        target_indices = list()
        for feature in user_feature_list:
            try:
                target_indices.append(user_feature_map[feature])
            except KeyError:
                print("new user feature encountered '{}'".format(feature))
                pass
        features = np.zeros(len(user_feature_map.keys()))
        for tar in target_indices:
            features[tar] = normalised_val
        features = sparse.csr_matrix(features)

    else:
        features = user_features
    t_idx = {value: key for key, value in item_map.items()}
    array_save = np.array([item_map[ind] for ind in df.index])
    scores = model.predict(user_id, array_save, user_features=features,
                           item_features=item_features, num_threads=12)
    sorted_scores = np.argsort(-scores)
    i_idx = [t_idx[array_save[x]] for x in sorted_scores]
    m = scores.max()
    mn = scores.min()
    for s in range(scores.shape[0]):
        scores[s] = (scores[s] - mn) / (m - mn)
    # scores = [scores[x] for x in sorted_scores]
    df["score"] = scores.tolist()
    top_items = df.loc[i_idx[0:k]]  # for now keep the top 50
    return top_items


def read_pickle(name):
    return pickle.load(open(name + ".pickle", "rb"))


def create_categories_form():
    global selected_city, df_new, df_explode, categories, to_show, form2, category_tuple
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
    category_tuple = (('', ''),)
    for j in range(len(to_show)):
        category_tuple = category_tuple + ((j, to_show[j]),)
    form2 = CategoryForm(Category=category_tuple)


def index(request):
    global selected_city, df_new, df_explode, categories, to_show, form2
    # This request happens each time the user selects a city from the dropdown list
    if request.method == 'POST':
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            selected_city = city_dict[int(request.POST["City"])]
            create_categories_form()
    # This request happens each time the user submits categories from the dropdown list

    else:
        form = CityForm(City=tuple_list)
        selected_city = city_dict[0]
        create_categories_form()
    vechiles = VechileForm()
    return render(request, 'rec/index.html', {'form': form, 'form2': form2, 'form4': vechiles})


def results(request):
    global df_new, cols, row_list, top_10_recommendations, origin, form2
    if request.method == 'POST':
        form2 = CategoryForm(Category=category_tuple, data=request.POST)
        if form2.is_valid():
            selected_category = request.POST.getlist('Category')
            selected_category = [to_show[int(s)] for s in selected_category]
            selected_vechile = int(request.POST.getlist('Vechile')[0])
            origin = (df_new.iloc[0].latitude, df_new.iloc[0].longitude)
            origin2 = [[df_new.iloc[0].longitude, df_new.iloc[0].latitude]]
            df_new = model_predict(df_new, 50, selected_category)
            dist, dur = Functions.calculate_distance_api(origin2, df_new[["longitude", "latitude"]],
                                                         selected_vechile)
            df_new["distance"] = dist
            dur = [d / 60 for d in dur]
            df_new["duration"] = dur
            top_10_recommendations = RecommenderEngine.get_recommendations_include_rating(df_new, selected_vechile)
            cols = ["Name", "Category", "Stars", "Distance(km)", "Duration(minutes)", "Score(%)"]
            name_list = top_10_recommendations.name.to_list()
            cat_list = top_10_recommendations.categories.to_list()
            star_list = top_10_recommendations.stars.to_list()
            distance_list = top_10_recommendations.distance.to_list()
            distance_list = ["{:.2f}".format(a) for a in distance_list]
            duration_list = top_10_recommendations.duration.to_list()
            duration_list = ["{}".format(math.ceil(a)) for a in duration_list]
            score_list = top_10_recommendations.score.to_list()
            score_list = ["{:.2f}".format(a) for a in score_list]
            row_list = []
            for m in range(len(name_list)):
                row_list.append({"name": name_list[m], "category": cat_list[m], "stars": star_list[m],
                                 "distance": distance_list[m], "duration": duration_list[m], "score": score_list[m]})
            return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})
    else:
        return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})


def show_map(request):
    map_path = 'rec/' + selected_city + '.html'
    Create_map.plot(top_10_recommendations, selected_city, origin, True)
    return render(request, map_path)


def register(request):
    if request.method == 'POST':
        print("It's a Post request")
    else:
        print("It's a GET request")
    return render(request, 'rec/register.html')


model = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/ligthFm_modelV4')
item_features = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/item_featuresV4')
user_features = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/user_featuresV4')
dataset = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/datasetV4')
item_map = dataset.mapping()[2]

df_b = Functions.read_business()
grouped = {k: set(v) for k, v in df_b.groupby('state')['city']}  # group by cities by state
grouped = {k: list(v) for k, v in grouped.items()}
tuple_list = (('', ''),)
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

df_new = df_explode = categories = to_show = form2 = cols = row_list = None  # initialize global variables
top_10_recommendations = origin = category_tuple = None
selected_city = city_dict[0]  # Choose the first available city to initialize index forms
create_categories_form()
