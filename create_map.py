import folium


class Create_map:
    def __init__(self):
        print("Create map initialized")

    @staticmethod
    def plot(df, city):
        filtered = df[df.city == city]
        filtered = filtered.filter(["name", "latitude", "longitude"])
        lat_list = filtered.latitude.to_list()
        long_list = filtered.longitude.to_list()
        names_list = filtered.name.to_list()
        my_map = folium.Map(location=[lat_list[0], long_list[0]], zoom_start=10, prefer_canvas=True)
        feature_group = folium.FeatureGroup("Locations")
        for lat, lng, name in zip(lat_list, long_list, names_list):
            feature_group.add_child(folium.CircleMarker(location=(lat, lng), popup=name, radius=6))
        my_map.add_child(feature_group)
        my_map.save(city + ".html")
