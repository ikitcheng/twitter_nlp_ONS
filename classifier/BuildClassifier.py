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
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve, accuracy_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import f1_score
import itertools
from collections import Counter
from imblearn.over_sampling import SMOTE
import pickle

# In[]:

class BuildClassifier:
    
    def __init__(self, csv_file):
        """
        Parameters
        ----------
        csv_file : string
            path to csv file containing features and labels.

        Returns
        -------
        None.

        """
        self.RSEED = 50
        self.df = pd.read_csv(csv_file, index_col=0)
        self.labels = np.array(self.df.pop('labels'))
        self.features = list(self.df.columns)

    
    def train_test_split(self, test_size=0.2):
        print('\n Split Data into Training and Testing Set...')
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.df, self.labels, stratify = self.labels,
            test_size = test_size, random_state = self.RSEED)
        print(f'Train data shape: {self.X_train.shape}')
        print(f'Test data shape: {self.X_test.shape}')
        print('\n ...Splitting complete!')

    
    def perform_SMOTE(self, X_train, y_train):
        # Balance training data to have equal numbers of each class
        sm = SMOTE(random_state=42)
        self.X_train_balanced, self.y_train_balanced = sm.fit_resample(X_train, 
                                                                       y_train)
            
        print('Resampled dataset shape %s' % Counter(self.y_train_balanced))
    
    def train_rf_model(self, X_train, y_train):
        # Create the model with 100 trees
        self.rf_model = RandomForestClassifier(n_estimators=100,
                                               bootstrap = True,
                                           criterion='gini',
                                           random_state=self.RSEED,
                                           max_features = 'sqrt',
                                           n_jobs=-1,
                                           verbose = 1)
        
        # Fit on training data
        self.rf_model.fit(X_train, y_train)
        
        # properties of RF
        n_nodes = []
        max_depths = []
        
        for ind_tree in self.rf_model.estimators_:
            n_nodes.append(ind_tree.tree_.node_count)
            max_depths.append(ind_tree.tree_.max_depth)
            
        print(f'___\nAverage number of nodes {int(np.mean(n_nodes))}___')
        print(f'___Average maximum depth {int(np.mean(max_depths))}___')
    
    def predict_train_test(self, model, X_train, X_test):
        # Assess performance of model
        self.pred_train = model.predict(X_train)
        self.prob_train = model.predict_proba(X_train)[:, 1]
        
        self.pred_test = model.predict(X_test)
        self.prob_test = model.predict_proba(X_test)[:, 1]
            
    def evaluate_model(self):
        """
        Compare machine learning model to baseline performance.
        Computes statistics and shows ROC curve.
        
        Parameters
        ----------
        pred_test : TYPE
            DESCRIPTION.
        prob_test : TYPE
            DESCRIPTION.
        pred_train : TYPE
            DESCRIPTION.
        prob_train : TYPE
            DESCRIPTION.
        smote : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """

        baseline = {}
        baseline['accuracy'] = accuracy_score(self.y_test, 
                                              [1 for _ in range(len(self.y_test))]) # always predict the majority class
        baseline['recall'] = recall_score(self.y_test, 
                                          [1 for _ in range(len(self.y_test))]) # always predict positive 
        baseline['precision'] = precision_score(self.y_test, 
                                                [1 for _ in range(len(self.y_test))]) # always predict positive
        baseline['roc'] = 0.5
        baseline['F1score'] = 2*0.5/(0.5+1)
        
        test_results = {}
        test_results['accuracy'] = accuracy_score(self.y_test, self.pred_test)
        test_results['recall'] = recall_score(self.y_test, self.pred_test)
        test_results['precision'] = precision_score(self.y_test, self.pred_test)
        test_results['roc'] = roc_auc_score(self.y_test, self.prob_test)
        test_results['F1score'] = f1_score(self.y_test, self.pred_test) # binary classifier
        
        train_results = {}
        train_results['accuracy'] = accuracy_score(self.y_train, self.pred_train)
        train_results['recall'] = recall_score(self.y_train, self.pred_train)
        train_results['precision'] = precision_score(self.y_train, self.pred_train)
        train_results['roc'] = roc_auc_score(self.y_train, self.prob_train)
        train_results['F1score'] = f1_score(self.y_train, self.pred_train)
        
        for metric in ['accuracy', 'recall', 'precision', 'roc', 'F1score']:
            print(f'\n{metric.capitalize()}\n'\
                  f'Baseline: {round(baseline[metric], 3)} | '\
                  f'Test: {round(test_results[metric], 3)} | '\
                  f'Train: {round(train_results[metric], 3)} ')
        
        # Calculate false positive rates and true positive rates
        base_fpr, base_tpr, _ = roc_curve(self.y_test, 
                                          [1 for _ in range(len(self.y_test))])
        model_fpr, model_tpr, _ = roc_curve(self.y_test, self.prob_test)
    
        plt.figure(figsize = (8, 6))
        plt.rcParams['font.size'] = 16
        
        # Plot both curves
        plt.plot(base_fpr, base_tpr, 'b', label = 'baseline')
        plt.plot(model_fpr, model_tpr, 'r', 
                 label = f"Random Forest (AUC = {test_results['roc']:.3f})")
        plt.legend()
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves')
    
    def calc_cm(self):
        # calculate confusion matrix 
        self.cm = confusion_matrix(self.y_test, self.pred_test)
        print(self.cm)
        TPR = self.cm[1][1]/(sum(self.cm[1]))
        TNR = self.cm[0][0]/(sum(self.cm[0]))
        FPR = 1 - TNR
        FNR = 1 - TPR
        print(f'TPR = {TPR:.2f} (Predicting correctly a user is bot)')
        print(f'TNR = {TNR:.2f} (Predicting correctly a user is individual)')
        print(f'FPR = {FPR:.2f} (Predicting incorrectly a user is bot)')
        print(f'FNR = {FNR:.2f} (Predicting incorrectly a user is human)')

    def plot_confusion_matrix(self, classes, normalize=False,
                              title='Confusion matrix',
                              cmap=plt.cm.Oranges):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        Source: http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
        """
        
        if normalize:
            self.cm = self.cm.astype('float') / self.cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')
    
        print(self.cm)
    
        plt.figure(figsize = (10, 8))
        plt.imshow(self.cm, interpolation='nearest', cmap=cmap)
        plt.title(title, size = 16)
        plt.colorbar(aspect=4)
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45, size = 14)
        plt.yticks(tick_marks, classes, size = 14)
    
        fmt = '.2f' if normalize else 'd'
        thresh = self.cm.max() / 2.
        
        # Labeling the plot
        for i, j in itertools.product(range(self.cm.shape[0]), range(self.cm.shape[1])):
            plt.text(j, i, format(self.cm[i, j], fmt), fontsize = 20,
                     horizontalalignment="center",
                     color="white" if self.cm[i, j] > thresh else "black")
            
        plt.grid(None)
        plt.tight_layout()
        plt.ylabel('True label', size = 16)
        plt.xlabel('Predicted label', size = 16)
        
    def create_fi_df(self, model):
        # Feature importance
        self.fi_df = pd.DataFrame({'feature': self.features,
                   'importance': model.feature_importances_}).\
                    sort_values('importance', ascending = False)
        print(self.fi_df.head(10))
        
    def plot_feature_importances(self):
        # Reset style 
        plt.figure()
        plt.style.use('default')
        
        # list of x locations for plotting
        importances = self.fi_df.importance
        x_values = list(range(len(importances)))
        
        # Make a bar chart
        plt.bar(x_values, importances, orientation = 'vertical', color = 'r',
                edgecolor = 'k', linewidth = 1.2)
        
        # Tick labels for x axis
        plt.xticks(x_values, self.fi_df.feature, rotation='vertical')
        
        # Axis labels and title
        plt.ylabel('Importance'); plt.xlabel('Variable'); 
        plt.title('Variable Importances');
        
        # List of features sorted from most to least important
        sorted_importances = self.fi_df.importance
        sorted_features = self.fi_df.feature
        
        # Cumulative importances
        cumulative_importances = np.cumsum(sorted_importances)
        
        # Make a line graph
        plt.plot(x_values, cumulative_importances, 'g-')
        
        # Draw line at 95% of importance retained
        plt.hlines(y = 0.95, xmin=0, xmax=len(sorted_importances),
                   color = 'r', linestyles = 'dashed')
    
        # Format x ticks and labels
        plt.xticks(x_values, sorted_features, rotation = 'vertical')
    
        # Axis labels and title
        plt.xlabel('Variable'); plt.ylabel('Cumulative Importance');
        plt.title('Cumulative Importances');
        plt.tight_layout()
        #plt.grid(True)
        
    def threshold_finder(self, required_fpr=None, required_tpr=None):
        """
        Tweeking the threshold for classifying positive
        E.g. threshold = 0.5 means if prob>0.5 then classify instance as positive.
        FPR leads to better precision (i.e. purer signal)

        Parameters
        ----------
        required_fpr : float
            The required fpr value.
        required_tpr : float
            The required tpr value. 
            
        Returns
        -------
        array
            Threshold values corresponding to fpr < required_fpr.
    
        """
        fpr, tpr, threshold = roc_curve(self.y_test, self.prob_test)
        if required_fpr:
            self.threshold_required = threshold[fpr < required_fpr]
        elif required_tpr:
            self.threshold_required = threshold[tpr > required_tpr]
    
    def predict_with_new_threshold(self, required_fpr=None, required_tpr=None):
        self.threshold_finder(required_fpr, required_tpr)
        if required_fpr:   
            self.pred_test = (self.prob_test>self.threshold_required[-1]).astype(int)
        elif required_tpr:
            self.pred_test = (self.prob_test>self.threshold_required[0]).astype(int)
    
    def save_model(self, model):
        # pickle the model for future use
        classifier_pkl = open('rf_classifier.pkl','wb')
        pickle.dump(model, classifier_pkl)
        classifier_pkl.close()
        print('Pickling complete.')

# In[]:

if __name__ == '__main__':
    # dataset 
    csv_file = '../../Datasets/user_classification/ind_vs_bot/dataset1and2/user_features_labels_noNan_dropped_boolean.csv'
    
    # instantiate class
    rf1 = BuildClassifier(csv_file)
    
    # split dataset
    rf1.train_test_split()
    
    # balance train dataset
    rf1.perform_SMOTE(rf1.X_train, rf1.y_train)
    
    # train model
    rf1.train_rf_model(rf1.X_train_balanced, rf1.y_train_balanced)
    
    # predict with trained model
    rf1.predict_train_test(rf1.rf_model ,rf1.X_train, rf1.X_test)
    
    # evaluate performance of trained model using roc curve
    rf1.evaluate_model()
    #plt.savefig('ROC_curve_rf_smote.png')
    #plt.close()
    
    # evaluate confusion matrix
    rf1.calc_cm()
    rf1.plot_confusion_matrix(classes = ['Individual', 'Bot'],
                              title = 'User Confusion Matrix')
    #plt.savefig('Confusion_matrix_rf_smote.png')
    #plt.close()
    
    # feature importance 
    rf1.create_fi_df(rf1.rf_model)
    rf1.plot_feature_importances()
    
    # change threshold
    #rf1.predict_with_new_threshold(required_fpr=0.05)
    #rf1.calc_cm()

    print('\n _______________ Testing on another dataset ________________')
    # df = pd.read_csv('../Datasets/user_classification/ind_vs_bot/dataset1/user_features_labels_noNan_dropped_fav_retweet_cols.csv', index_col=0)
    # labels = np.array(df1.pop('labels'))
    # rf_pred = rf1.rf_model.predict(df1)
    # cm = confusion_matrix(labels, rf_pred)
    # print(cm)

