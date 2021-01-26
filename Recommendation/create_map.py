import folium
from folium.plugins import Search
import requests
import math
import pathlib


class Create_map:
    def __init__(self):
        print("Create map initialized")

    @staticmethod
    def directions(origin, dest, vechile, name):
        body = {"coordinates": [origin, dest], "instructions": "false", "units": "m"}
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': '5b3ce3597851110001cf6248a22eebae30af4b398201ada78e405dba',
            'Content-Type': 'application/json; charset=utf-8'
        }
        if vechile == 0:
            call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body,
                                 headers=headers)
        else:
            call = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body,
                                 headers=headers)
        call_json = call.json()
        summary = call_json['features'][0]['properties']['summary']
        del call_json['features'][0]['properties']['summary']
        distance = summary['distance'] / 1000
        duration = summary['duration'] / 60
        call_json['features'][0]['properties']['Distance'] = "{:.2f} km".format(distance)
        call_json['features'][0]['properties']['Duration'] = "{} min".format(math.ceil(duration))
        my_map = folium.Map(location=[origin[1], origin[0]], zoom_start=15, prefer_canvas=True)
        geo = folium.GeoJson(call_json, name="Directions",
                             tooltip=folium.GeoJsonTooltip(fields=['Distance', 'Duration']))
        mark = folium.FeatureGroup("User Location")
        mark.add_child(
            folium.Marker((origin[1], origin[0]), icon=folium.Icon(color='red', icon='map-marker', prefix='fa'),
                          tooltip="Origin"))
        mark2 = folium.FeatureGroup("Destination")
        mark2.add_child(
            folium.Marker((dest[1], dest[0]), icon=folium.Icon(color='blue', icon='map-marker', prefix='fa'),
                          tooltip=name))
        my_map.add_child(geo)
        my_map.add_child(mark)
        my_map.add_child(mark2)
        folium.LayerControl().add_to(my_map)
        # my_map.save(str(pathlib.Path().absolute()) + "/rec/templates/rec/" + name + ".html")
        return my_map

    @staticmethod
    def plot(df, city, user, include=False):
        """This function will be used to plot the recommended places
        I have to add at the html:"""
        # var geojsonMarkerOptions = {
        #     radius: 6,
        #     fillColor: "#ff7800",
        #     color: "#000",
        #     weight: 1,
        #     opacity: 1,
        #     fillOpacity: 0.8
        # };
        # var geo_json_81ba1ab92ce54e2e9b4f488fdcddaff5 = L.geoJson(null, {
        #     onEachFeature: geo_json_81ba1ab92ce54e2e9b4f488fdcddaff5_onEachFeature,
        #     pointToLayer: function(feature, latlng) {
        # return L.circleMarker(latlng, geojsonMarkerOptions);
        # },
        fields = ["Name", "City", "Stars"]
        if include:
            fields.append("Preference")
            fields.append("Distance")
        filtered = df[df.city == city]
        filtered = filtered.filter(["name", "latitude", "longitude", "city", "stars", "distance"])
        lat_list = filtered.latitude.to_list()
        long_list = filtered.longitude.to_list()
        names_list = filtered.name.to_list()
        city_list = filtered.city.to_list()
        stars_list = filtered.stars.to_list()
        distance_list = filtered.distance.to_list()
        for i in range(len(distance_list)):
            distance_list[i] = "{:.2f}".format(distance_list[i])
        position = range(1, len(stars_list) + 1)
        my_map = folium.Map(location=[lat_list[0], long_list[0]], zoom_start=10, prefer_canvas=True)
        my_list = list()
        for lat, lng, name, city, star, i, distance in zip(lat_list, long_list, names_list,
                                                           city_list, stars_list, position, distance_list):
            my_dict = dict()
            my_dict["type"] = "Feature"
            my_dict["geometry"] = {"type": "Point", "coordinates": [lng, lat]}
            my_dict["properties"] = {"Name": name, "City": city, "Stars": star, "Preference": i, "Distance": distance}
            my_list.append(my_dict)
        geojson_file = dict()
        geojson_file["type"] = "FeatureCollection"
        geojson_file["features"] = my_list
        geo = folium.GeoJson(geojson_file, name="Location",
                             tooltip=folium.GeoJsonTooltip(fields=fields))
        mark = folium.FeatureGroup("User Location")
        mark.add_child(folium.CircleMarker(user, radius=10))
        my_map.add_child(mark)
        my_map.add_child(geo)
        Search(
            layer=geo,
            geom_type='Point',
            placeholder='Search for a place',
            search_label="Name",
            search_zoom=18,
            collapsed=False,
        ).add_to(my_map)
        folium.LayerControl().add_to(my_map)
        # my_map.save(str(pathlib.Path().absolute()) + "/rec/templates/rec/" + city + ".html")
        return my_map
