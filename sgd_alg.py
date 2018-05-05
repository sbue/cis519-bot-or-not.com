import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier
import math
import pickle


def save_obj(obj, name):
    with open('/Users/manewilliams/Desktop/School/Cis519/Project/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('/Users/manewilliams/Desktop/School/Cis519/Project/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

users = load_obj('users_features')
num_users = len(users.keys())
print("Number of users: "+str(num_users))
bots = load_obj('bots_features')
num_bots = len(bots.keys())
print("Number of bots: "+str(num_bots))


def train(fold, num_folds, predictor):
    user_range_min = int(num_users*(fold-1)/num_folds)
    user_range_max = int(num_users*fold/num_folds)
    train_x = []
    train_y = []
    for user in list(users.keys())[user_range_min:user_range_max]:
        train_x.append(users[user])
        train_y.append(0)
    bot_range_min = int(num_bots*(fold-1)/num_folds)
    bot_range_max = int(num_bots*fold/num_folds)
    for bot in list(bots.keys())[bot_range_min:bot_range_max]:
        train_x.append(bots[bot])
        train_y.append(1)
    predictor.fit(train_x, train_y)
    return predictor

def test(fold, num_folds, predictor):
    correct = 0
    incorrect = 0
    user_range_min = int(num_users*(fold-1)/num_folds)
    user_range_max = int(num_users*fold/num_folds)
    for user in list(users.keys())[user_range_min:user_range_max]:
        prediction = predictor.predict([users[user]])
        if prediction == 0:
            correct += 1
        else:
            incorrect += 1
    bot_range_min = int(num_bots*(fold-1)/num_folds)
    bot_range_max = int(num_bots*fold/num_folds)
    for bot in list(bots.keys())[bot_range_min:bot_range_max]:
        prediction = predictor.predict([bots[bot]])
        if prediction == 1:
            correct += 1
        else:
            incorrect += 1
    return correct, incorrect


def test_sgd(a, e, t, eta):
    total_right = 0
    total_wrong = 0
    accuracies = []
    for x in range(1, 6):
        clf = SGDClassifier(loss='log', alpha = a, max_iter = 1000, tol = t, epsilon = e, learning_rate='constant', eta0 = eta)
        feature_set = []
        badge_set = []
        for y in range(1, 6):
            if x != y:
                clf = train(y, 5, clf)
        right, wrong = test(x, 5, clf)

        total_right += right
        total_wrong += wrong
        acc = right / (right + wrong)
        print("Fold #"+str(x)+" Accuracy: "+str(acc))
    overall_acc = total_right / (total_right + total_wrong)
    print("\nOverall Accuracy: "+str(overall_acc))


# TODO: adjust parameters for better results, or change the learning algorithm
best_alpha = 0.0076
best_epsilon = 1.6
best_tol = 0.008
best_eta0 = 0.03
test_sgd(best_alpha, best_epsilon, best_tol, best_eta0)





