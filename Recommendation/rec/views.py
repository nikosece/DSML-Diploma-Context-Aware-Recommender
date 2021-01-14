from django.shortcuts import render
# from django.http import HttpResponseRedirect
from .forms import CityForm, CategoryForm, ChoiceForm
from recommender_engine import RecommenderEngine
from functions import Functions
from create_map import Create_map
from lightfm.data import Dataset
from lightfm import LightFM
import numpy as np
# import Rec_fx as rf
import pickle
import sys
from scipy import sparse
import os.path
from os import path


def save_pickle(var, name):
    with open(name + '.pickle', 'wb') as fle:
        pickle.dump(var, fle, protocol=pickle.HIGHEST_PROTOCOL)


def model_predict(df, k=50, tags=None, user_id=None):
    if user_id is None:
        inverse_user_feature_map = {value: key for key, value in dataset.mapping()[1].items()}
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
    choices = ChoiceForm()
    return render(request, 'rec/index.html', {'form': form, 'form2': form2, 'form3': choices})


def results(request):
    global df_new, cols, row_list, top_10_recommendations, origin, form2
    if request.method == 'POST':
        form2 = CategoryForm(Category=category_tuple, data=request.POST)
        if form2.is_valid():
            selected_category = request.POST.getlist('Category')
            selected_category = [to_show[int(s)] for s in selected_category]
            selected_category_join = ", ".join(selected_category)  # Combine all selected categories into one string
            selected_filter = int(request.POST.getlist('Filter')[0])
            origin = (df_new.iloc[0].latitude, df_new.iloc[0].longitude)
            if selected_filter == 2:
                df_new = model_predict(df_new, 50, selected_category)
                df_new["distance"] = df_new.apply(
                    lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
                    axis=1)
                top_10_recommendations = RecommenderEngine.get_recommendations_include_rating(df_new)
            elif selected_filter == 0:
                df_new["distance"] = df_new.apply(
                    lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
                    axis=1)
                top_10_recommendations = RecommenderEngine.get_recommendations_include_rating(df_new, [selected_category_join])
            else:
                df_new["distance"] = df_new.apply(
                    lambda row: Functions.calculate_distance(origin, (row['latitude'], row['longitude'])),
                    axis=1)
                top_10_recommendations = model_predict(df_new, 10, selected_category)
            cols = ["Name", "Category", "Stars", "Distance", "Score"]
            name_list = top_10_recommendations.name.to_list()
            cat_list = top_10_recommendations.categories.to_list()
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
    else:
        return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})


def show_map(request):
    map_path = 'rec/' + selected_city + '.html'
    if not path.exists(
            "/home/anonymous/Documents/Diploma-Recommender/Recommendation/rec/templates/rec/" + selected_city +
            '.html'):
        Create_map.plot(top_10_recommendations, selected_city, origin, True)
    return render(request, map_path)


model = read_pickle("/home/anonymous/Documents/ligthFm_modelV4")
interactions = read_pickle('/home/anonymous/Documents/interactionsV4')
weights = read_pickle('/home/anonymous/Documents/weights')
item_features = read_pickle('/home/anonymous/Documents/item_featuresV4')
user_features = read_pickle('/home/anonymous/Documents/user_featuresV4')
dataset = read_pickle('/home/anonymous/Documents/datasetV4')
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

df_new = df_explode = categories = to_show = form2 = cols = row_list = top_10_recommendations = origin = category_tuple = None
selected_city = city_dict[0]  # Choose the first available city to initialize index forms
create_categories_form()
