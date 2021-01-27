from django.shortcuts import render, redirect
from django.db.models import Count
from .forms import CityForm, CategoryForm, VechileForm, SignUpForm, BusinessForm, ReviewForm, ProfileForm
from .models import BusinessCity, BusinessState, Business, Review
from django.contrib.auth import login, authenticate
from django.contrib import messages
from recommender_engine import RecommenderEngine
from functions import Functions
from create_map import Create_map
from sql_func import Sqlfunctions
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
    array_save = np.array([item_map[ind.business_id] for ind in df])
    scores = model.predict(user_id, array_save, user_features=features,
                           item_features=item_features, num_threads=12)
    m = scores.max()
    mn = scores.min()
    for s in range(scores.shape[0]):
        scores[s] = (scores[s] - mn) / (m - mn)
    # scores = [scores[x] for x in sorted_scores]
    for i in range(len(df)):
        df[i].score = scores[i]
    top_items = sorted(df, key=lambda x: x.score, reverse=True)
    return top_items[0:k]


def read_pickle(name):
    return pickle.load(open(name + ".pickle", "rb"))


def create_categories_form():
    global selected_city, df_new, df_explode, categories, to_show, form2, category_tuple
    df_new = Business.objects.filter(city__name=selected_city)
    categories = [i['categories__name'] for i in df_new.values('categories__name')
                                                     .annotate(total=Count('categories__name'))
                                                     .order_by('-total')[0:61]]
    to_show = []
    for c in categories:
        if c in cols_to_show:
            to_show.append(c)
    category_tuple = (('', ''),)
    for j in to_show:
        category_tuple = category_tuple + ((j, j),)
    form2 = CategoryForm(Category=category_tuple)


def index(request):
    global selected_city, df_new, df_explode, categories, to_show, form2
    # This request happens each time the user selects a city from the dropdown list
    if request.method == 'POST':
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            selected_city = request.POST["City"]
            create_categories_form()
    # This request happens each time the user submits categories from the dropdown list

    else:
        form = CityForm(City=tuple_list)
        create_categories_form()
    vechiles = VechileForm()
    return render(request, 'rec/index.html', {'form': form, 'form2': form2, 'form4': vechiles})


def results(request):
    global df_new, cols, row_list, top_10_recommendations, origin, form2, selected_vechile
    if request.method == 'POST':
        form2 = CategoryForm(Category=category_tuple, data=request.POST)
        if form2.is_valid():
            selected_category = request.POST.getlist('Category')
            selected_category = [s for s in selected_category]
            selected_vechile = int(request.POST.getlist('Vechile')[0])
            origin = (df_new[0].latitude, df_new[0].longtitude)
            origin2 = [[df_new[0].longtitude, df_new[0].latitude]]
            df_new = model_predict(list(df_new), 50, selected_category)
            dist, dur = Functions.calculate_distance_api(origin2, df_new,  # this is 90 % of running time
                                                         selected_vechile)
            dur = [d / 60 for d in dur]
            for i in range(len(df_new)):
                df_new[i].distance = dist[i]
                df_new[i].duration = dur[i]
            top_10_recommendations = RecommenderEngine.get_recommendations_include_rating(df_new, selected_vechile)
            cols = ["Name", "Category", "Stars", "Distance(km)", "Duration(minutes)", "Score(%)", "Directions"]
            name_list = top_10_recommendations.name.to_list()
            cat_list = top_10_recommendations.categories.to_list()
            star_list = top_10_recommendations.stars.to_list()
            distance_list = top_10_recommendations.distance.to_list()
            distance_list = ["{:.2f}".format(a) for a in distance_list]
            duration_list = top_10_recommendations.duration.to_list()
            duration_list = ["{}".format(math.ceil(a)) for a in duration_list]
            score_list = top_10_recommendations.score.to_list()
            score_list = ["{:.2f}".format(a) for a in score_list]
            ids_list = list(range(0, 10))
            row_list = []
            for m in range(len(name_list)):
                row_list.append(
                    {"name": name_list[m], "category": cat_list[m], "stars": star_list[m], "id": ids_list[m],
                     "distance": distance_list[m], "duration": duration_list[m], "score": score_list[m]})
            return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})
    else:
        return render(request, 'rec/results.html', {'header': cols, 'rows': row_list})


def show_map(request):
    m = Create_map.plot(top_10_recommendations, selected_city, origin, True)
    m = m._repr_html_()
    return render(request, 'rec/map.html', {'map': m})


def show_directions(request, b_id):
    df = top_10_recommendations.iloc[b_id]
    name = df['name']
    dest = [df.longitude, df.latitude]
    origin2 = [origin[1], origin[0]]
    m = Create_map.directions(origin2, dest, selected_vechile, name)
    m = m._repr_html_()
    return render(request, 'rec/map.html', {'map': m})


def show_business(request, b_id):
    df = top_10_recommendations.iloc[b_id]
    bus_id = df.id
    b = Business.objects.get(business_id=bus_id)
    bar = [100 * x / b.review_count for x in b.stars_count]
    name = b.name
    dest = [df.longitude, df.latitude]
    m = Create_map.business([origin[1], origin[0]], dest, name)
    # splitted = m[0].split("\n")
    # for line in range(len(splitted)):
    #     if "<style>html," in splitted[line]:
    #         to_del = line
    # del splitted[to_del]
    # m[0] = "\n".join(splitted)

    return render(request, 'rec/show_business.html', {'map': m, 'b': b, 'bar': bar})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Registration Success')
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'rec/signup.html', {'form': form})


def review(request):
    if request.method == 'POST':
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            selected_review_city = request.POST["City"]
            # df = Functions.filtering_city(df_b, selected_review_city)
            df = Business.objects.filter(city__name=selected_review_city)
            b_names = [d.name for d in df]  # i can do this with database
            b_ids = [d.business_id for d in df]
            b_ids = [x for _, x in sorted(zip(b_names, b_ids))]
            b_names.sort()
            business_tuple = (('', ''),)
            for j in range(len(b_names)):
                business_tuple = business_tuple + ((b_ids[j], b_names[j]),)
            form_b = BusinessForm(Business=business_tuple)
            # create_categories_form()
    # This request happens each time the user submits categories from the dropdown list

    else:
        form = CityForm(City=tuple_list)
        form_b = BusinessForm(Business=(('', ''),))
    return render(request, 'rec/review.html', {'form': form, 'form2': form_b})


def apply_review(request):
    global selected
    if request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            r_star = int(form.cleaned_data['stars'])  # user review stars
            old_star_count = selected.stars_count  # number of each star before this review
            check_review = Review.objects.filter(user=request.user, business=selected)
            if len(check_review) == 0:  # user review this business for first time
                instance = form.save(commit=False)
                instance.user = request.user
                instance.business = selected
                instance.save()
                avg_star = round((float(selected.stars) * selected.review_count + r_star)
                                 / (selected.review_count + 1), 1)
                selected.review_count = selected.review_count + 1
            else:  # use had already review this business before
                check_review = check_review[0]
                old_star_value = int(check_review.stars)
                form = ReviewForm(request.POST, instance=check_review)
                old_star_count[old_star_value - 1] = old_star_count[old_star_value - 1] - 1
                avg_star = round((float(selected.stars) * selected.review_count + r_star - old_star_value)
                                 / selected.review_count, 1)
                form.save()
            messages.success(request, 'Your review was stored successfully')
            old_star_count[r_star - 1] = old_star_count[r_star - 1] + 1
            selected.stars_count = old_star_count
            selected.stars = avg_star
            selected.save()
            return redirect("index")
    else:
        b_id = request.GET["Business"]
        selected = Business.objects.get(business_id=b_id)
        bar = [100 * x / selected.review_count for x in selected.stars_count]
        form = ReviewForm()
    return render(request, 'rec/apply_review.html', {'b': selected, 'form': form, 'bar': bar})


def show_profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was updated successfully')
            return redirect("index")
    else:
        signed = request.user
        form = ProfileForm(initial={'email': signed.email, 'first_name': signed.first_name,
                                    'last_name': signed.last_name,
                                    'preference': signed.preference})
        return render(request, 'rec/profile.html', {'form': form})


# if request.user.is_authenticated:
#     print(type(current_user.preference[0]))
model = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/ligthFm_modelV4')
item_features = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/item_featuresV4')
user_features = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/user_featuresV4')
dataset = read_pickle(str(pathlib.Path().absolute()) + '/Dataset/datasetV4')
item_map = dataset.mapping()[2]

df_b = Functions.read_business()
tuple_list = Sqlfunctions.state_city_group()
df_new = df_explode = categories = to_show = form2 = cols = row_list = None  # initialize global variables
top_10_recommendations = origin = category_tuple = selected = selected_vechile = None
selected_city = tuple_list[0][0]  # Choose the first available city to initialize index forms
cols_to_show = set([i['categories__name'] for i in Business.objects.values('categories__name')
                   .annotate(total=Count('categories__name'))
                   .order_by('-total')[0:61]])
create_categories_form()
# states = df_b.state.unique()
# for s in states:
#     print(s)
