from django.shortcuts import render, redirect
from django.db.models import Count
from .forms import CityForm, CategoryForm, VechileForm, SignUpForm, BusinessForm, ReviewForm, ProfileForm
from .models import BusinessCity, Business, Review
from django.contrib.auth import login, authenticate
from django.contrib import messages
from recommender_engine import RecommenderEngine
from functions import Functions
from pandas import json_normalize
from create_map import Create_map
import numpy as np
import math
import pandas as pd
import pickle
from scipy import sparse
import pathlib


def row_result_create(df):
    name_list = df.name.to_list()
    cat_list = df.categories.to_list()
    star_list = df.stars.to_list()
    distance_list = df.distance.to_list()
    distance_list = ["{:.2f}".format(a) for a in distance_list]
    duration_list = df.duration.to_list()
    duration_list = ["{}".format(math.ceil(a)) for a in duration_list]
    score_list = df.score.to_list()
    score_list = ["{:.2f}".format(a) for a in score_list]
    ids_list = list(range(0, len(distance_list)))
    b_id_list = df.id.to_list()
    r_count_list = df.r_count.to_list()
    address_list = df.address.to_list()
    row_list = []
    for m in range(len(name_list)):
        row_list.append(
            {"name": name_list[m], "category": cat_list[m], "stars": star_list[m], "id": ids_list[m],
             "distance": distance_list[m], "duration": duration_list[m], "score": score_list[m],
             "r_count": r_count_list[m], 'b_id': b_id_list[m], 'address': address_list[m]})
    return row_list


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


def create_categories_form(request):
    if request.session['selected_city'] != 'Όλες':
        filtered = Business.objects.filter(city__name=request.session['selected_city']).order_by(
            '-review_count').filter(
            review_count__gte=100)
        request.session['df_new'] = [i.business_id for i in filtered]
    else:
        filtered = Business.objects.filter(review_count__gte=100).order_by('-review_count')
        request.session['df_new'] = [i.business_id for i in filtered]
    request.session['categories'] = [i['categories__name'] for i in filtered.values('categories__name')
        .annotate(total=Count('categories__name'))
        .order_by('-total')]
    request.session['category_tuple'] = (('', ''),)
    for j in request.session['categories']:
        request.session['category_tuple'] = request.session['category_tuple'] + ((j, j),)
    return CategoryForm(Category=request.session['category_tuple'])


def index(request):
    # This request happens each time the user selects a city from the dropdown list
    if request.method == 'POST':
        form = CityForm(City=tuple_list, data=request.POST)
        if form.is_valid():
            request.session['selected_city'] = request.POST["City"]
            form2 = create_categories_form(request)
    # This request happens each time the user submits categories from the dropdown list

    else:
        form = CityForm(City=tuple_list)
        request.session['category_tuple'] = (('', ''),)
        form2 = CategoryForm(Category=request.session['category_tuple'])
    vechiles = VechileForm()
    return render(request, 'rec/index.html', {'form': form, 'form2': form2, 'form4': vechiles})


def results(request, sort_type=None):
    if sort_type:
        name_map = {"distance": "Απόσταση", "stars": "Βαθμολογία", "score": "Προκαθορισμένο",
                    "r_count": "Πλήθος κριτικών"}
        top_10_recommendations = pd.DataFrame(columns=request.session['columns'])
        values = request.session['top_10_recommendations']
        for i in values:
            top_10_recommendations = top_10_recommendations.append(pd.DataFrame([i], columns=top_10_recommendations.columns), ignore_index=True)
        if sort_type == 'distance':
            top_10_recommendations = top_10_recommendations.sort_values(by=[sort_type])
        else:
            top_10_recommendations = top_10_recommendations.sort_values(by=[sort_type], ascending=False)
        row_list = row_result_create(top_10_recommendations)
        request.session['row_list'] = row_list
        request.session['sort'] = name_map[sort_type]

        return render(request, 'rec/results.html', {'rows': row_list, 'sort': name_map[sort_type]})
    if request.method == 'POST':
        form2 = CategoryForm(Category=request.session['category_tuple'], data=request.POST)
        if form2.is_valid():
            selected_category = request.POST.getlist('Category')
            selected_category = [s for s in selected_category]
            selected_vechile = int(request.POST.getlist('Vechile')[0])
            request.session['selected_vechile'] = selected_vechile
            loc = request.POST.getlist('Location')[0]
            loc = loc.split("_")
            us_lat = float(loc[1])
            us_lot = float(loc[0])
            origin = (us_lot, us_lat)
            origin2 = [[us_lat, us_lot]]
            request.session['origin'] = origin
            request.session['origin2'] = origin
            df_new = Business.objects.filter(business_id__in=request.session['df_new'])
            df_new = RecommenderEngine.similarity_filter(list(df_new), 50, [", ".join(selected_category)])
            # df_new = model_predict(list(df_new), 50, selected_category)
            dist, dur = Functions.calculate_distance_api(origin2, df_new,  # this is 90 % of running time
                                                         selected_vechile)
            dur = [d / 60 for d in dur]
            for i in range(len(df_new)):
                df_new[i].distance = dist[i]
                df_new[i].duration = dur[i]
            top_10_recommendations = RecommenderEngine.get_recommendations_include_rating(df_new, selected_vechile)
            request.session['top_10_recommendations'] = top_10_recommendations.values.tolist()
            request.session['columns'] = list(top_10_recommendations.columns)
            row_list = row_result_create(top_10_recommendations)
            request.session['row_list'] = row_list
            request.session['sort'] = "Προκαθορισμένο"
            return render(request, 'rec/results.html', {'rows': row_list, 'sort': "Προκαθορισμένο"})
    else:
        return render(request, 'rec/results.html', {'rows': request.session['row_list'], 'sort': request.session['sort']})


def show_map(request):
    top_10_recommendations = pd.DataFrame(columns=request.session['columns'])
    values = request.session['top_10_recommendations']
    for i in values:
        top_10_recommendations = top_10_recommendations.append(
            pd.DataFrame([i], columns=top_10_recommendations.columns), ignore_index=True)
    m = Create_map.plot(top_10_recommendations, request.session['selected_city'], request.session['origin'], True)
    m = m._repr_html_()
    return render(request, 'rec/map.html', {'map': m})


def show_directions(request, b_id):
    top_10_recommendations = pd.DataFrame(columns=request.session['columns'])
    values = request.session['top_10_recommendations']
    for i in values:
        top_10_recommendations = top_10_recommendations.append(
            pd.DataFrame([i], columns=top_10_recommendations.columns), ignore_index=True)
    df = top_10_recommendations.iloc[b_id]
    name = df['name']
    dest = [df.longitude, df.latitude]
    origin2 = [request.session['origin'][1], request.session['origin'][0]]
    m = Create_map.directions(origin2, dest, request.session['selected_vechile'], name)
    m = m._repr_html_()
    return render(request, 'rec/map.html', {'map': m})


def show_business(request, b_id):
    b = Business.objects.get(business_id=b_id)
    name = b.name
    dest = [b.longtitude, b.latitude]
    m = Create_map.business(dest, name)
    # splitted = m[0].split("\n")
    # for line in range(len(splitted)):
    #     if "<style>html," in splitted[line]:
    #         to_del = line
    # del splitted[to_del]
    # m[0] = "\n".join(splitted)

    return render(request, 'rec/show_business.html', {'map': m, 'b': b})


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
            if selected_review_city != 'Όλες':
                df = Business.objects.filter(city__name=selected_review_city).order_by('-review_count')
            else:
                df = Business.objects.order_by('-review_count')
            b_names = [d.name for d in df]  # i can do this with database
            b_ids = [d.business_id for d in df]
            # b_ids = [x for _, x in sorted(zip(b_names, b_ids))]    This is for name sort, above i do review sort
            # b_names.sort()
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


def apply_review(request, b_id=None):
    global selected
    if request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            r_star = int(form.cleaned_data['stars'])  # user review stars
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
                avg_star = round((float(selected.stars) * selected.review_count + r_star - old_star_value)
                                 / selected.review_count, 1)
                form.save()
            messages.success(request, 'Your review was stored successfully')
            selected.stars = avg_star
            selected.save()
            return redirect("index")
    else:
        if b_id is None:
            b_id = request.GET["Business"]
        selected = Business.objects.get(business_id=b_id)
        form = ReviewForm()
    return render(request, 'rec/apply_review.html', {'b': selected, 'form': form})


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


def show_reviews(request):
    reviews = Review.objects.filter(user=request.user).order_by('-updated')
    reviews = list(reviews)[0:5]
    return render(request, 'rec/my_reviews.html', {'reviews': reviews})


cities = BusinessCity.objects.order_by('name').values()
tuple_list = (('', ''), ('Όλες', 'Όλες'),)
for c_ity in cities:
    tuple_list = tuple_list + ((c_ity['name'], c_ity['name']),)

# tuple_list = None # to filled up
