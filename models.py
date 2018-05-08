import numpy as np
from sklearn import tree
from sklearn.utils import shuffle
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import math
import pickle


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

users = list(load_obj('users_features_v3').values())
num_users = len(users)
print("Number of users: "+str(num_users))
bots = list(load_obj('bots_features_v3').values())
num_bots = len(bots)
print("Number of bots: " + str(num_bots))

X = users + bots
Y = [0 for _ in range(num_users)] + [1 for _ in range(num_bots)]
X, Y = shuffle(X, Y, random_state=42)
X, Y = shuffle(X, Y, random_state=42)
X, Y = shuffle(X, Y, random_state=42)

def get_model_cv_accuracy(model, num_folds=5):
    scores = cross_val_score(model, X, Y, cv=num_folds)
    print(f'Fold accuracies are: {scores}')
    print(f'Overall Accuracy is {scores.mean()}')


def test_sgd(a, e, t, eta):
    clf = SGDClassifier(loss='log', alpha = a, max_iter = 1000, tol = t, epsilon = e, learning_rate='constant', eta0 = eta)
    get_model_cv_accuracy(clf)

def test_rf(max_depth=3):
	clf = RandomForestClassifier(max_depth=max_depth, random_state=0)
	get_model_cv_accuracy(clf)


# TODO: adjust parameters for better results, or change the learning algorithm
best_alpha = 0.0076
best_epsilon = 1.6
best_tol = 0.008
best_eta0 = 0.03
# test_sgd(best_alpha, best_epsilon, best_tol, best_eta0)
for i in range(2, 20):
	print(f'max_depth: {i}')
	test_rf(max_depth=i)



