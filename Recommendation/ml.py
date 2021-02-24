import timeit
import os
from rec.models import BusinessCategory, Business

from lightfm.data import Dataset


def save_pickle(var, name):
    import pickle
    with open(name + '.pickle', 'wb') as fle:
        pickle.dump(var, fle, protocol=pickle.HIGHEST_PROTOCOL)


def read_pickle(name):
    import pickle
    return pickle.load(open(name + ".pickle", "rb"))


def get_all_categories():
    cats = BusinessCategory.objects.all()
    all_cats = set()
    for c in cats:
        all_cats.add(c.name)
    return all_cats


def get_business_categories(b):
    cats = set()
    for c in b.categories.all():
        cats.add(c)
    return cats


def create_features():
    from rec.models import BusinessCategory, Business
    cats = BusinessCategory.objects.all()
    all_cats = set()
    for c in cats:
        all_cats.add(c.name)
    all_businesses = Business.objects.all()
    my_dict = {}
    for b in all_businesses:
        cats = set()
        for c in b.categories.all():
            cats.add(c.name)
        c_dict = {}
        for c in all_cats:
            if c in cats:
                c_dict[c] = 1
            # else:
            #     c_dict[c] = 0
        my_dict[b.business_id] = c_dict
    return my_dict


def get_similar_tags(model, tag_id):
    import numpy as np
    tag_embeddings = (model.item_embeddings[2222:].T
                      / np.linalg.norm(model.item_embeddings[2222:], axis=1)).T
    query_embedding = tag_embeddings[tag_id]
    similarity = np.dot(tag_embeddings, query_embedding)
    most_similar = np.argsort(-similarity)[1:3]
    return most_similar


def execute_tags():
    dataset = read_pickle('/home/anonymous/Documents/Diploma-Recommender/Recommendation/lightfm/dataset')
    tag_labels = dataset.mapping()[3]
    reverse = {}
    for key, value in tag_labels.items():
        reverse[value] = key
    tag_ids = range(2222, 2227)
    for tag_id in tag_ids:
        print('Most similar tags for %s: %s' % (reverse[tag_id],
                                                [reverse[x + 2222] for x in get_similar_tags(model, tag_id - 2222)]))


def split_data(interaction):
    import numpy as np
    from lightfm.cross_validation import random_train_test_split
    seed = 123
    train1, test1 = random_train_test_split(interaction, test_percentage=0.2, random_state=np.random.RandomState(seed))

    print('The dataset has %s users and %s items, '
          'with %s interactions in the test and %s interactions in the training set.'
          % (train1.shape[0], train1.shape[1], test1.getnnz(), train1.getnnz()))

    a = train1.multiply(test1).nnz == 0  # make sure train and test are truly disjoint
    print(a)
    return train1, test1


def collaborative(train, test):
    from lightfm import LightFM
    import timeit
    import pickle
    from lightfm.evaluation import precision_at_k
    from lightfm.evaluation import auc_score
    NUM_THREADS = 12
    NUM_COMPONENTS = 21
    NUM_EPOCHS = 16
    ITEM_ALPHA = 5.97967e-6
    learning_rate = 0.033
    k = 5
    model = LightFM(loss='warp', random_state=123,
                    item_alpha=ITEM_ALPHA,
                    no_components=NUM_COMPONENTS,
                    learning_rate=learning_rate)

    start1 = timeit.default_timer()
    model = model.fit(train, epochs=NUM_EPOCHS, num_threads=NUM_THREADS)
    end = timeit.default_timer()
    print("Training time: {} secs.".format(end - start1))
    # Compute and print the AUC score
    train_auc = auc_score(model, train, num_threads=NUM_THREADS).mean()
    print('Collaborative filtering train AUC: %s' % train_auc)

    test_auc = auc_score(model, test, num_threads=NUM_THREADS).mean()
    print('Collaborative filtering test AUC: %s' % test_auc)

    print("Train precision: %.4f" % precision_at_k(model, train, k=k, num_threads=NUM_THREADS).mean())
    print("Test precision: %.4f" % precision_at_k(model, test, train_interactions=train, k=k,
                                                  num_threads=NUM_THREADS).mean())
    # save_pickle(model, './lightfm/google_colaborative')
    with open('./lightfm/google_colaborative' + '.pickle', 'wb') as fle:
        pickle.dump(model, fle, protocol=pickle.HIGHEST_PROTOCOL)


def hybrid(train, test, item_features):
    import timeit
    import pickle
    from lightfm import LightFM
    from lightfm.evaluation import precision_at_k
    from lightfm.evaluation import auc_score
    NUM_THREADS = 12
    NUM_COMPONENTS = 42
    NUM_EPOCHS = 14
    ITEM_ALPHA = 0.000256
    learning_rate = 0.0529
    k = 5
    # Let's fit a WARP model
    model = LightFM(loss='warp', random_state=123,
                    item_alpha=ITEM_ALPHA,
                    no_components=NUM_COMPONENTS,
                    learning_rate=learning_rate)
    start1 = timeit.default_timer()
    model = model.fit(train, item_features=item_features, epochs=NUM_EPOCHS,
                      num_threads=NUM_THREADS)
    end1 = timeit.default_timer()
    print("Training time: {} secs.".format(end1 - start1))
    # Compute and print the AUC score
    train_auc = auc_score(model, train, item_features=item_features,
                          num_threads=NUM_THREADS).mean()
    print('Hybrid model filtering train AUC: %s' % train_auc)

    test_auc = auc_score(model, test, item_features=item_features,
                         train_interactions=train, num_threads=NUM_THREADS).mean()
    print('Hybrid model filtering test AUC: %s' % test_auc)

    print(
        "Train precision: %.4f" % precision_at_k(model, train, item_features=item_features,
                                                 k=k, num_threads=NUM_THREADS).mean())
    print("Test precision: %.4f" % precision_at_k(model, test, item_features=item_features,
                                                  train_interactions=train, k=k, num_threads=NUM_THREADS).mean())
    # save_pickle(model, './lightfm/google_model')
    with open('./lightfm/google_model' + '.pickle', 'wb') as fle:
        pickle.dump(model, fle, protocol=pickle.HIGHEST_PROTOCOL)


df_r = read_pickle("/home/anonymous/Documents/Diploma-Recommender/dataframe")
flag = True
for file in os.listdir("./lightfm"):
    if file == 'dataset.pickle':
        flag = False
if flag:
    dataset = Dataset()
    cats = BusinessCategory.objects.all()
    all_cats = []
    for c in cats:
        all_cats.append(c.name)
    dataset.fit(users=df_r.user_id, items=df_r.business_id, item_features=all_cats)
    save_pickle(dataset, './lightfm/dataset')
else:
    dataset = read_pickle('./lightfm/dataset')
num_users, num_items = dataset.interactions_shape()
print('Num users: {}, num_items {}.'.format(num_users, num_items))
print('Creating interactions')
flag = True
for file in os.listdir("./lightfm"):
    if file == 'google_interactions.pickle':
        flag = False
if flag:
    (interactions, weights) = dataset.build_interactions([(x['user_id'],
                                                           x['business_id']) for index, x in df_r.iterrows()])
    save_pickle(interactions, './lightfm/google_interactions')
else:
    interactions = read_pickle('./lightfm/google_interactions')

print('Interactions created successfully')

train, test = split_data(interactions)
flag = True
for file in os.listdir("./lightfm"):
    if file == 'google_colaborative.pickle':
        flag = False
if flag:
    collaborative(train, test)

flag = True
for file in os.listdir("./lightfm"):
    if file == 'google_model.pickle':
        flag = False
if flag:
    start = timeit.default_timer()
    print("Item Features creation started")
    features = create_features()
    print("check")
    item_features = dataset.build_item_features(((business_id,
                                                  value)
                                                 for business_id, value in features.items()))
    print("Item Features took: {}".format(timeit.default_timer() - start))
    hybrid(train, test, item_features)
