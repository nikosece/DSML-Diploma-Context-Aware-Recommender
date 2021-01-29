import requests
import json
import pickle
import time


def save_pickle(var, name):
    with open(name + '.pickle', 'wb') as fle:
        pickle.dump(var, fle, protocol=pickle.HIGHEST_PROTOCOL)


def deletion(a, b):
    del_list = set()
    for i in a:
        for j in range(len(b)):
            if i['place_id'] == b[j]['place_id']:
                del_list.add(j)
    b = [i for j, i in enumerate(b) if j not in del_list]
    a.extend(b)
    return a


def get_data(latitude, longitude, radius, search, pagetoken=None):
    api_key = 'AIzaSyDZVMPpjO-_nBgUkWc-9VWUnFxyo0LBbqI'
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    url = url + 'location=' + latitude + ',' + longitude + '&radius=' + radius + '&type=' + search + '&key=' + api_key
    if pagetoken:
        url = url + '&pagetoken=' + pagetoken
    time.sleep(2.5)
    r = requests.get(url)
    x = r.json()
    y = x['results']
    if 'next_page_token' in x:
        y_new = get_data(latitude, longitude, radius, search, x['next_page_token'])
        y.extend(y_new)
        return y
    else:
        return y


with open('requests') as f:
    for line in f:
        *arg, area = line.rstrip('\n').split(" ")
        search_type = 'cafe'
        y_c = get_data(*arg, search_type)
        search_type = 'restaurant'
        y_r = get_data(*arg, search_type)
        y_c = deletion(y_c, y_r)
        search_type = 'bar'
        y_b = get_data(*arg, search_type)
        y_c = deletion(y_c, y_b)
        save_pickle(y_c, area)
        print("Total businesses: ",len(y_c))
