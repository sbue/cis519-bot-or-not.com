import numpy as np
from sklearn import tree
from sklearn.utils import shuffle
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler  
import math
import pickle


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

users = list(load_obj('users_features_v4').values())
num_users = len(users)
print("Number of users: "+str(num_users))
bots = list(load_obj('bots_features_v4').values())
num_bots = len(bots)
print("Number of bots: " + str(num_bots))

X = users + bots
Y = [0 for _ in range(num_users)] + [1 for _ in range(num_bots)]
X, Y = shuffle(X, Y, random_state=42)
X, Y = shuffle(X, Y, random_state=42)
X, Y = shuffle(X, Y, random_state=42)

def get_model_cv_accuracy(model, num_folds=5, scale=False):
    global X
    global Y
    if scale:
        scaler = StandardScaler()
        scaler.fit(X)  
        X = scaler.transform(X)
    scores = cross_val_score(model, X, Y, cv=num_folds)
    print(f'Fold accuracies are: {scores}')
    print(f'Overall Accuracy is {scores.mean()}')


def test_sgd(loss='perceptron', penalty='l1', alpha=10, rate='optimal', eta=0.03):
    clf = SGDClassifier(loss=loss, penalty=penalty, alpha=alpha, learning_rate=rate, max_iter=20000, tol=0.001, eta0=eta, random_state=1)
    get_model_cv_accuracy(clf)

def test_rf(n_est=16, max_depth=9):
	clf = RandomForestClassifier(n_estimators=n_est, max_depth=max_depth, random_state=0)
	get_model_cv_accuracy(clf)

def test_nn(solver='adam', alpha=1, hidden_layer=(2, 4, 2)):
    clf = MLPClassifier(solver=solver, alpha=alpha, hidden_layer_sizes=hidden_layer, max_iter=1000, random_state=1)
    get_model_cv_accuracy(clf, scale=True)

def test_gbdt(l='deviance', rate=0.1, n_est=100, depth=3):
    clf = GradientBoostingClassifier(loss=l, learning_rate=rate, n_estimators=n_est, max_depth=depth, random_state=1)
    get_model_cv_accuracy(clf)


print("SGD:")
test_sgd()
print("Random Forest:")
test_rf()
print("Boosted Decision Trees:")
test_gbdt()
print("Neural Network:")
test_nn()




