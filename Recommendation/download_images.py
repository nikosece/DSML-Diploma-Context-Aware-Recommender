from rec.models import Business
import time
import os
import requests

got_them = set()
for file in os.listdir("./"):
    if file.endswith(".jpg"):
        got_them.add(file.split(".")[0])
all_businesses = list(Business.objects.all())
key = 'AIzaSyDZVMPpjO-_nBgUkWc-9VWUnFxyo0LBbqI'
for b in all_businesses:
    ref = b.photo.photo_reference
    if ref not in got_them:
        url = "https://maps.googleapis.com/maps/api/place/photo?maxheight="
        url = url + str(b.photo.height)
        url = url + "&photoreference="
        url = url + ref
        url = url + "&key=" + key
        r = requests.get(url)
        with open(ref + '.jpg', 'wb') as img_file:
            img_file.write(r.content)
        time.sleep(1.5)
