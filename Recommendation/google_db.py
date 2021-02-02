from rec.models import Business, BusinessCity, BusinessCategory, BusinessPrice, BusinessPhoto, BusinessIcon
import os
import pickle
businesses = pickle.load(open("DB_backup.pickle","rb"))
cities = set()
categories = set()
icons = set()
price_level = set()
for key, item in businesses.items():
	cities.add(item['city'])
	icons.add(item['icon'])
	price_level.add(item['price_level'])
	for c in item['categories']:
		categories.add(c)
cities = list(cities)
cities.sort()
categories = list(categories)
categories.sort()
icons = list(icons)
icons.sort()
price_level = list(price_level)
price_level.sort()

cities_dict = {}
categories_dict = {}
icons_dict = {}
price_level_dict = {}

for c in cities:
	obj = BusinessCity(name=c)
	obj.save()
	cities_dict[c] = obj

for c in categories:
	obj = BusinessCategory(name=c)
	obj.save()
	categories_dict[c] = obj

for c in icons:
	obj = BusinessIcon(name=c)
	obj.save()
	icons_dict[c] = obj

for c in price_level:
	obj = BusinessPrice(name=c)
	obj.save()
	price_level_dict[c] = obj


for key, b in businesses.items():
	foto = BusinessPhoto(height=b['photos']['height'],width=b['photos']['width'], html_attributions=b['photos']['html_attributions'],photo_reference=b['photos']['html_attributions'])
	foto.save()
	cat_list = []
	for cat in b['categories']:
	   cat_list.append(categories_dict[cat])
	lat = b['lat']
	lng = b['lng']
	b=Business(name=b['name'], address=b['vicinity'], business_id=key, latitude=lat, longtitude=lng,stars=b['rating'],review_count=b['user_ratings_total'], city=cities_dict[b['city']], icon=icons_dict[b['icon']], price_level=price_level_dict[b['price_level']],photo=foto)
	b.save()
	for c in cat_list:
	   b.categories.add(c)
	b.save()



# ### QUERIES ####

# # 1) get Business by id:
# selected = Business.objects.get(business_id='HMoD2-LuoiAiE3wQHuibJg')

# # 2) Get all categories from selected business:
# for c in selected.categories.all():
# 	print(c.name)			


# # 3) Get all businesses for a specific category:
# selected = BusinessCategory.objects.get(name='shopping_mall')
# for b in selected.business_set.all():
# 	print(b)


# # 4) Count number of businesses having that category
# selected.business_set.all().count()

# ## At foreign keys i have added related name and query name so the query will be
# # 5) 
# selected = BusinessCity.objects.get(name='Calgary')		# i select a city
# selected.businesses.filter(name="Pizza Hut")			# Get businesses at calgary with name Pizza Hut

# # 6) Get all businesses for a specific city
# Business.objects.filter(city__name="Calgary")

# # 7) Filter both a businesses and foreign key field
# Business.objects.filter(name="Pizza Hut",city__name="Calgary")	# Pizza hut at calgary

# # 8) adding Many to many filter
# Business.objects.filter(city__name="Calgary",categories__name__in=["Bars"]) # !!!! When using IN, it is like OR operator

# # 9 ) Double filter
# Business.objects.filter(city__name="Calgary",categories__name__in=["Bars"]).filter(categories__name__in=["Chinese"])

# # 10) review filter
# review = Review.objects.filter(user__email='tzagarakis3@gmail.com', business__business_id='HMoD2-LuoiAiE3wQHuibJg')
#  # 11) top 60 categories
#  result = Business.objects.values('categories__name').annotate(total=Count('categories__name')).order_by('-total')[0:61]

# (Business.objects.values('city','state').annotate(total=Count('business_id'))



# cat_to_show = set(i['categories__name'] for i in [df_new.values('categories__name')
#                    .annotate(total=Count('categories__name'))
#                    .order_by('-total')[0:61]])





# def directions(origin, dest, vechile, name):
# 	body = {"coordinates": [origin, dest],"instructions":"false", "units":"km"}
# 	headers = {
# 	    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
# 	    'Authorization': '5b3ce3597851110001cf6248a22eebae30af4b398201ada78e405dba',
# 	    'Content-Type': 'application/json; charset=utf-8'
# 	}
# 	if vechile == 0:
# 	    call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body,
# 	                         headers=headers)
# 	else:
# 	    call = requests.post('https://api.openrouteservice.org/v2/directions/foot-walking/geojson', json=body,
# 	                         headers=headers)
# 	call_json = call.json()
# 	summary = call_json['features'][0]['properties']['summary']
# 	del call_json['features'][0]['properties']['summary']
# 	distance = summary['distance']
# 	duration = summary['duration']/60
# 	call_json['features'][0]['properties']['Distance'] = "{:.2f} km".format(distance)
# 	call_json['features'][0]['properties']['Duration'] = "{} min".format(math.ceil(duration))
# 	my_map = folium.Map(location=[origin[1], origin[0]], zoom_start=15, prefer_canvas=True)
# 	geo = folium.GeoJson(call_json, name="Directions",
# 	                     tooltip=folium.GeoJsonTooltip(fields=['Distance', 'Duration']))
# 	mark = folium.FeatureGroup("User Location")
# 	mark.add_child(
# 	    folium.Marker((origin[1], origin[0]), icon=folium.Icon(color='red', icon='map-marker', prefix='fa'),
# 	                  tooltip="Origin"))
# 	mark2 = folium.FeatureGroup("Destination")
# 	mark2.add_child(
# 	    folium.Marker((dest[1], dest[0]), icon=folium.Icon(color='blue', icon='map-marker', prefix='fa'),
# 	                  tooltip=name))
# 	my_map.add_child(geo)
# 	my_map.add_child(mark)
# 	my_map.add_child(mark2)
# 	folium.LayerControl().add_to(my_map)
# 	my_map.save('test.html')




# call = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body, headers=headers)


# user = CustomUser.objects.get(email='tzagarakis3@gmail.com')
# reviews = Review.objects.filter(user=user)
# reviews[0].updated.strftime("%d/%m/%Y")


# df2 = df.pivot_table(index=['business_id'], columns=['review_stars'], values='count').fillna(0)
# df3= df.groupby(['business_id']).agg(['count'])
# df.pivot_table(index=['business_id'], columns='review_stars', aggfunc='size', fill_value=0)
# pd.crosstab([df.business_id], df.review_stars)


# ArrayField(models.PositiveIntegerField(),size=5,)
# ids = Business.objects.all().values_list('business_id', flat=True)


# for id, value in my_dict.items():
#     Business.objects.filter(business_id=id).update(stars_count=value)




# round(sum([i * j for i, j in zip(b.stars_count, b)])/b.review_count,1)

# Burgers
# Business.objects.filter(Q(name__contains="Burger")|Q(name__contains="burger"))

# # Count for each city the total number of burger stores

# cols_to_show = list([(i['city__name'],i['total']) for i in Business.objects.filter(Q(name__contains="Burger")|Q(name__contains="burger")).values('city__name')
#                     .annotate(total=Count('city__name'))
#                     .order_by('-total')])


### εχω βγαλει ψητοπωλεια και γνωστες αλυσιδες take away cafe