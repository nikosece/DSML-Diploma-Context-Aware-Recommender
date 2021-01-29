import json
import folium
from folium.plugins import Search
import os
import pickle


def read_pickle(name):
    return pickle.load(open(name, "rb"))


def plot(df):
    fields = ["Name", "Stars", "Review Count"]
    lat_list = df[0]
    long_list = df[1]
    names_list = df[2]
    stars_list = df[3]
    count_list = df[4]
    my_map = folium.Map(location=[lat_list[0], long_list[0]], zoom_start=12, prefer_canvas=True)
    my_list = list()
    for lati, lng, name, star, count in zip(lat_list, long_list, names_list, stars_list, count_list):
        my_dict = dict()
        my_dict["type"] = "Feature"
        my_dict["geometry"] = {"type": "Point", "coordinates": [lng, lati]}
        my_dict["properties"] = {"Name": name, "Stars": star, "Review Count": count}
        my_list.append(my_dict)
    geojson_file = dict()
    geojson_file["type"] = "FeatureCollection"
    geojson_file["features"] = my_list
    geo = folium.GeoJson(geojson_file, name="Location",
                         tooltip=folium.GeoJsonTooltip(fields=fields))
    my_map.add_child(geo)
    Search(
        layer=geo,
        geom_type='Point',
        placeholder='Search for a place',
        search_label="Name",
        search_zoom=18,
        collapsed=False,
    ).add_to(my_map)
    mark = folium.FeatureGroup("Borders")
    with open('track_requests') as f:
        for line in f:
            *arg, area = line.rstrip('\n').split(" ")
            mark.add_child(folium.Circle((arg[0], arg[1]), radius=arg[2]))
    my_map.add_child(mark)
    folium.LayerControl().add_to(my_map)
    my_map.save("map.html")


res = []
for file in os.listdir("./"):
    if file.endswith(".pickle"):
        if len(res) == 0:
            res = read_pickle(file)
        else:
            res.extend(read_pickle(file))

lat = []
lot = []
names = []
stars = []
r_count = []
print("Total results: ", len(res))
for r in res:
    lat.append(r['geometry']['location']['lat'])
    lot.append(r['geometry']['location']['lng'])
    names.append(r['name'])
    try:
        stars.append(r['rating'])
    except KeyError:
        stars.append("None")
    try:
        r_count.append(r['user_ratings_total'])
    except KeyError:
        r_count.append("None")
plot([lat, lot, names, stars, r_count])
