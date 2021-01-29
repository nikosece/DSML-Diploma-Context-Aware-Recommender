import json
import folium
from folium.plugins import Search
import os
import pickle


def read_pickle(name):
    return pickle.load(open(name, "rb"))


def plot2(df, my_map, feature_name):
    fields = ["Name", "Stars", "Review Count"]
    lat_list = df[0]
    long_list = df[1]
    names_list = df[2]
    stars_list = df[3]
    count_list = df[4]
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
    geo = folium.GeoJson(geojson_file, name=feature_name,
                         tooltip=folium.GeoJsonTooltip(fields=fields), show=False)
    my_map.add_child(geo)
    return my_map


def plot():
    mark = folium.FeatureGroup("Borders")
    with open('track_requests') as f:
        for line in f:
            *arg, area = line.rstrip('\n').split(" ")
            mark.add_child(folium.Circle((arg[0], arg[1]), radius=arg[2]))
    my_map = folium.Map(location=[arg[0], arg[1]], zoom_start=12, prefer_canvas=True)
    my_map.add_child(mark)
    return my_map


all_res = []
area_names = []
for file in os.listdir("./"):
    if file.endswith(".pickle"):
        all_res.append(read_pickle(file))
        area_names.append(file.strip(".pickle"))
init_map = plot()
all_res = [x for _, x in sorted(zip(area_names, all_res))]
area_names.sort()
for res, display in zip(all_res, area_names):
    lat = []
    lot = []
    names = []
    stars = []
    r_count = []
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
    init_map = plot2([lat, lot, names, stars, r_count], init_map, display)
# Search(
#     layer=geo,
#     geom_type='Point',
#     placeholder='Search for a place',
#     search_label="Name",
#     search_zoom=18,
#     collapsed=False,
# ).add_to(init_map)

folium.LayerControl().add_to(init_map)
init_map.save("map.html")
