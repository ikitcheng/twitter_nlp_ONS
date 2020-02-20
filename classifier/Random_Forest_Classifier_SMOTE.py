# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 10:19:29 2020

@author: I Kit Cheng
"""

# In[]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import f1_score
import itertools
from collections import Counter
from imblearn.over_sampling import SMOTE
import pickle

# In[]:

# Set random seed to ensure reproducible runs
RSEED = 50

# Dataset
df = pd.read_csv('../../Datasets/user_classification/ind_vs_org/dataset2/user_features_labels_noNan_dropped_fav_retweet_cols.csv', index_col=0) 



print('\n _______________________ Split Data into Training and Testing Set __________________________')
# Extract the labels
labels = np.array(df.pop('labels'))

# 30% examples in test data
train, test, train_labels, test_labels = train_test_split(df, labels, 
                                                          stratify = labels,
                                                          test_size = 0.3, 
                                                          random_state = RSEED)

# In[]:
# Features for feature importances
features = list(train.columns)

print(f'Train data shape: {train.shape}')
print(f'Test data shape: {test.shape}')

# In[]:

print('\n _______________________ Evaluate the Decision Tree _______________________')
def evaluate_model(predictions, probs, train_predictions, train_probs, smote=False):
    """Compare machine learning model to baseline performance.
    Computes statistics and shows ROC curve."""
    
    baseline = {}
    
    baseline['recall'] = recall_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['precision'] = precision_score(test_labels, [1 for _ in range(len(test_labels))])
    baseline['roc'] = 0.5
    
    results = {}
    
    results['recall'] = recall_score(test_labels, predictions)
    results['precision'] = precision_score(test_labels, predictions)
    results['roc'] = roc_auc_score(test_labels, probs)
    
    train_results = {}
    if smote:
        train_results['recall'] = recall_score(train_labels_res, train_predictions)
        train_results['precision'] = precision_score(train_labels_res, train_predictions)
        train_results['roc'] = roc_auc_score(train_labels_res, train_probs)
    else:
        train_results['recall'] = recall_score(train_labels, train_predictions)
        train_results['precision'] = precision_score(train_labels, train_predictions)
        train_results['roc'] = roc_auc_score(train_labels, train_probs)
    
    for metric in ['recall', 'precision', 'roc']:
        print(f'{metric.capitalize()} Baseline: {round(baseline[metric], 2)} Test: {round(results[metric], 2)} Train: {round(train_results[metric], 2)}')
    
    # Calculate false positive rates and true positive rates
    base_fpr, base_tpr, _ = roc_curve(test_labels, [1 for _ in range(len(test_labels))])
    model_fpr, model_tpr, _ = roc_curve(test_labels, probs)

    plt.figure(figsize = (8, 6))
    plt.rcParams['font.size'] = 16
    
    # Plot both curves
    plt.plot(base_fpr, base_tpr, 'b', label = 'baseline')
    plt.plot(model_fpr, model_tpr, 'r', label = 'model')
    plt.legend()
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate'); plt.title('ROC Curves')

# In[]:

print('\n _______________________ Confusion matrix _______________________')


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Oranges):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    Source: http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.figure(figsize = (10, 10))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, size = 24)
    plt.colorbar(aspect=4)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45, size = 14)
    plt.yticks(tick_marks, classes, size = 14)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    
    # Labeling the plot
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt), fontsize = 20,
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
        
    plt.grid(None)
    plt.tight_layout()
    plt.ylabel('True label', size = 18)
    plt.xlabel('Predicted label', size = 18)
# In[]:
print('\n _______________________ Random Forest + SMOTE _______________________')


sm = SMOTE(random_state=42)
train_res, train_labels_res = sm.fit_resample(train, train_labels)
print('Resampled dataset shape %s' % Counter(train_labels_res))

# In[]:
print('\n _______________________ Training 100 Trees _______________________')

# Create the model with 100 trees
model = RandomForestClassifier(n_estimators=100, 
                               random_state=RSEED, 
                               max_features = 'sqrt',
                               n_jobs=-1, verbose = 1)

# Fit on training data
model.fit(train_res, train_labels_res)

# In[]:
n_nodes = []
max_depths = []

for ind_tree in model.estimators_:
    n_nodes.append(ind_tree.tree_.node_count)
    max_depths.append(ind_tree.tree_.max_depth)
    
print(f'Average number of nodes {int(np.mean(n_nodes))}')
print(f'Average maximum depth {int(np.mean(max_depths))}')

# In[]:
print('\n _______________________ Assess Random Forest Performance _______________________')
train_rf_predictions = model.predict(train_res)
train_rf_probs = model.predict_proba(train_res)[:, 1]

rf_predictions = model.predict(test)
rf_probs = model.predict_proba(test)[:, 1]

evaluate_model(rf_predictions, rf_probs, train_rf_predictions, train_rf_probs, smote=True)
plt.savefig('ROC_curve_rf_smote.png')
plt.close()

print('\n _______________________ Confusion matrix _______________________')
cm = confusion_matrix(test_labels, rf_predictions)
plot_confusion_matrix(cm, classes = ['Individual', 'Organisation'],
                      title = 'User Confusion Matrix') 
plt.savefig('Confusion_matrix_rf_smote.png')
plt.close()

print(f"f1score = {f1_score(test_labels, rf_predictions, average='binary')}") # labels binary
print(f1_score(test_labels, rf_predictions, average='micro')) # global metric 
print(f'TPR = {cm[1][1]/(sum(cm[1])):.2f} (Predicting correctly a user is organisation)')
print(f'TNR = {cm[0][0]/(sum(cm[0])):.2f} (Predicting correctly a user is individual)')
# In[]:
print('\n _______________________ Feature Importances _______________________')
fi_model = pd.DataFrame({'feature': features,
                   'importance': model.feature_importances_}).\
                    sort_values('importance', ascending = False)
print(fi_model.head(10))

def plot_feature_importances(fi_model):
    # Reset style 
    plt.style.use('default')
    
    # list of x locations for plotting
    importances = fi_model.importance
    x_values = list(range(len(importances)))
    
    # Make a bar chart
    plt.bar(x_values, importances, orientation = 'vertical', color = 'r', edgecolor = 'k', linewidth = 1.2)
    
    # Tick labels for x axis
    plt.xticks(x_values, fi_model.feature, rotation='vertical')
    
    # Axis labels and title
    plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances');
    
    # List of features sorted from most to least important
    sorted_importances = fi_model.importance
    sorted_features = fi_model.feature
    
    # Cumulative importances
    cumulative_importances = np.cumsum(sorted_importances)
    
    # Make a line graph
    plt.plot(x_values, cumulative_importances, 'g-')
    
    # Draw line at 95% of importance retained
    plt.hlines(y = 0.95, xmin=0, xmax=len(sorted_importances), color = 'r', linestyles = 'dashed')
    
    # Format x ticks and labels
    plt.xticks(x_values, sorted_features, rotation = 'vertical')
    
    # Axis labels and title
    plt.xlabel('Variable'); plt.ylabel('Cumulative Importance'); plt.title('Cumulative Importances');
    plt.tight_layout()
    plt.grid(True)
    
plot_feature_importances(fi_model)
# In[]:
print('\n _______________________ Testing on another dataset _______________________')
df1 = pd.read_csv('../Datasets/user_classification/ind_vs_bot/dataset1/user_features_labels_noNan_dropped_fav_retweet_cols.csv', index_col=0)
labels1 = np.array(df1.pop('labels'))
rf_predictions1 = model.predict(df1)
cm = confusion_matrix(labels1, rf_predictions1)
plot_confusion_matrix(cm, classes = ['Individual', 'Organisation'],
                      title = 'User Confusion Matrix') 
plt.savefig('Confusion_matrix_rf1_smote.png')
plt.close()

# In[]:
print('\n _______________________ Pickle the model _______________________')

rf_bot_classifier_pkl = open('rf_smote_org_classifier.pkl','wb')
pickle.dump(model, rf_bot_classifier_pkl)
rf_bot_classifier_pkl.close()
print('Pickling complete.')

# In[]:
print('\n _______________________ Unpickle the model _______________________')
model_pkl = open('rf_smote_bot_classifier.pkl','rb')
model = pickle.load(model_pkl)
