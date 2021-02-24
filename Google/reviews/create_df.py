import pickle
import os
import pandas as pd


def get_keys():
    all_res1 = []
    all_files = []
    for file in os.listdir("./"):
        if file.endswith(".pickle"):
            all_res1.append(file.split(".")[0])
            all_files.append(pickle.load(open(file, "rb")))
    return all_res1, all_files


names, files = get_keys()
df = []
for name, f in zip(names, files):
    for row in f['Reviews']:
        a = row
        a['business_id'] = name
        df.append(a)
df = pd.DataFrame(df)
