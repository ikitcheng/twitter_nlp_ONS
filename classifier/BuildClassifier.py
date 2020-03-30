# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 10:19:29 2020

@author: I Kit Cheng
"""

# In[]:

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, label_binarize, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve, auc 
from sklearn.metrics import f1_score, recall_score, precision_score, make_scorer, accuracy_score, roc_auc_score
from sklearn.metrics import precision_recall_fscore_support, classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier, plot_importance, to_graphviz, plot_tree
from sklearn.ensemble import VotingClassifier, GradientBoostingClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RandomizedSearchCV
import itertools
from itertools import cycle
from collections import Counter
from imblearn.over_sampling import SMOTE
from sklearn.utils import resample
from numpy import interp
from scipy.stats import uniform, randint
import pickle
plt.style.use('default')
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
        self.labels = np.array(self.df.labels)
        self.X = self.df.loc[:, self.df.columns != 'labels']
        self.features = list(self.X)
        
        # initiate classifiers 
        self.rf_model = RandomForestClassifier(n_estimators=100,
                                               bootstrap = True,
                                               criterion='gini',
                                               random_state=self.RSEED,
                                               max_features = 'sqrt',
                                               n_jobs=-1,
                                               verbose = 1,
                                               class_weight="balanced")
        self.et_model = ExtraTreesClassifier(n_estimators=500,
                                             n_jobs=-1,
                                             random_state=self.RSEED)
        self.gb_model = GradientBoostingClassifier(n_estimators=100,
                                                   random_state=self.RSEED)
        self.xgb_model = XGBClassifier(n_estimators=100,
                                       random_state=self.RSEED)
        self.knn_model = KNeighborsClassifier(n_neighbors=5)
        self.svm_model = SVC(gamma='auto', probability=True)
        self.lr_model = LogisticRegression(random_state=42)
        self.lda_model = LinearDiscriminantAnalysis()
        self.nb_model = GaussianNB()
        self.ensemble_model = VotingClassifier(
            estimators=[('lr', self.lr_model), 
                        ('rf', self.rf_model), 
                        ('et', self.et_model),
                        ('svm', self.svm_model), 
                        ('lda', self.lda_model)], voting='soft')
        self.pipeline = Pipeline([('scaler', StandardScaler())])
    
    def class_distribution(self):
        plt.figure()
        sns.countplot(x=self.labels, color='black')
        plt.title('Class distribution', fontsize=16)
        plt.ylabel('Class Counts', fontsize=16)
        plt.xlabel('Class Label', fontsize=16)
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        
    def binarize_output(self):
        self.labels = label_binarize(self.labels, 
                                     classes=list(
                                         np.unique(self.labels).astype(int)))
        
    def split_train_test(self, test_size=0.2):
        print('\n Split Data into Training and Testing Set...')
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.labels, stratify = self.labels,
            test_size = test_size, random_state = self.RSEED) # stratify means train and test sample have same proportions of each class
        print(f'Train data shape: {self.X_train.shape}')
        if np.ndim(self.labels) == 1: 
            print(f'Train class distribution:\n{pd.Series(self.y_train).value_counts(normalize=True)}')
        print(f'Test data shape: {self.X_test.shape}')
        if np.ndim(self.labels) == 1:
            print(f'Test class distribution:\n{pd.Series(self.y_test).value_counts(normalize=True)}')
        print('\n ...Splitting complete!')
    
    def resample(self, method='smote'):
        """

        Parameters
        ----------
        method : string, optional
            Resampling method: 'smote', 'up', 'down'. The default is 'smote'.
            This is to be used after split_train_test() method.
        Returns
        -------
        None.

        """
        if method == 'SMOTE':
            # Balance training data to have equal numbers of each class
            sm = SMOTE(random_state=42)
            self.X_train_balanced, self.y_train_balanced = sm.fit_resample(self.X_train, 
                                                                           self.y_train)
                    
        elif method == 'up':
            # recombine training features and labels into a single df
            self.train_df = self.X_train.copy()
            self.train_df['labels'] = self.y_train
            
            # majority class
            self.train_df0 = self.train_df[self.train_df.labels==0]
            n_samples_maj = max(self.train_df.labels.value_counts())
            
            # upsample minority classes
            self.train_df1 = resample(self.train_df[self.train_df.labels==1], 
                            replace=True,             # sample with replacement
                            n_samples=n_samples_maj,  # to match majority class
                            random_state=42)
            
            self.train_df2 = resample(self.train_df[self.train_df.labels==2], 
                            replace=True,             # sample with replacement
                            n_samples=n_samples_maj,  # to match majority class
                            random_state=42)
            
            # Combine majority class with upsampled minority class
            self.train_df_balanced = pd.concat([self.train_df0, 
                                          self.train_df1,
                                          self.train_df2])
            self.y_train_balanced = np.array(self.train_df_balanced.labels)
            self.X_train_balanced = self.train_df_balanced.loc[:, 
                                   self.train_df_balanced.columns != 'labels']
            
        print(f'Resampled dataset shape {Counter(self.y_train_balanced)}')
        
    def feature_scaling(self):
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)
        print('Feature scaling complete!')
        
    def k_fold_cv(self, model, k=10, balanced=False):
        # Cross-validation using cross_val_score
        print(f'\n Split Data into {k-1} Training and 1 Validation Set...')
        self.start = time.time()
        if balanced:
            self.f1scores_cv = cross_val_score(model, 
                                                     self.X_train_balanced,
                                                     self.y_train_balanced, 
                                                     cv=10,
                                                     scoring='f1_weighted')
        else:
            self.f1scores_cv = cross_val_score(model,
                                                     self.X_train,
                                                     self.y_train,
                                                     cv=10,
                                                     scoring='f1_weighted')
            
        
        print(f'Mean F1 score: {self.f1scores_cv.mean():.4f} +- '
              f'{self.f1scores_cv.std():.4f}')
        self.time_taken = time.time() - self.start
        print(f"Time taken: {self.time_taken:.4f}s")
        
        # Cross-validation using stratifiedKFold
        # self.scores_kfold_cv = []
        # skf = StratifiedKFold(n_splits=k, random_state=self.RSEED, shuffle=True)
        # for train_index, test_index in skf.split(X, y):
        #     #print("TRAIN:", train_index, "TEST:", test_index)
        #     X_train, X_test = X.values[train_index], X.values[test_index]
        #     y_train, y_test = y[train_index], y[test_index]
        #     self.best_model.fit(X_train,y_train)
        #     self.scores_kfold_cv.append(self.best_model.score(X_test,y_test))
    
    def train_model(self, clf, balanced=False):
        # Fit clf model on training data
        self.start = time.time()
        if balanced:
            clf.fit(self.X_train_balanced, self.y_train_balanced)
        else:
            clf.fit(self.X_train, self.y_train)
        
        self.time_taken = time.time() - self.start
        print(f"Time taken: {self.time_taken:.4f}s")
            
    def get_rf_properties(self, model):
        # properties of RF
        n_nodes = []
        max_depths = []
        
        for ind_tree in model.estimators_:
            n_nodes.append(ind_tree.tree_.node_count)
            max_depths.append(ind_tree.tree_.max_depth)
            
        print(f'___\nAverage number of nodes {int(np.mean(n_nodes))}___')
        print(f'___Average maximum depth {int(np.mean(max_depths))}___')
        
    def train_predict_evaluate_OneVsRestClassifier(self, estimator):
        # Learn to predict each class against the other
        random_state = np.random.RandomState(0)
        self.OVRClassifier = OneVsRestClassifier(estimator)
        self.OVRClassifier.fit(self.X_train, self.y_train)
        self.pred_test = self.OVRClassifier.predict(self.X_test)
        self.prop_test = self.OVRClassifier.predict_proba(self.X_test)
        
        # Compute ROC curve, ROC-AUC, precision-recall curve for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        precision = dict()
        recall = dict()
        
        for i in range(n_classes):
            # roc curve and roc-auc
            fpr[i], tpr[i], _ = roc_curve(self.y_test[:, i], self.prop_test[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
            # This is the same as doing:
            roc_auc[i] = roc_auc_score(self.y_test[:,i],self.prop_test[:,i],'macro') # roc_auc for ith class
            
            # precision-recall
            precision[i], recall[i], _ = precision_recall_curve(self.y_test[:, i],
                                                                self.prop_test[:, i])
            plt.plot(recall[i], precision[i], lw=2, label='class {}'.format(i))
       
        # precision recall curve  
        plt.xlabel("recall")
        plt.ylabel("precision")
        plt.legend(loc="best")
        plt.title("precision vs. recall curve")
        plt.show()
        
        # Compute micro-average ((global metric) ROC curve and ROC area
        # ref: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
        fpr["micro"], tpr["micro"], _ = roc_curve(self.y_test.ravel(), self.prop_test.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
        
        # This is the same as doing:
        roc_auc['micro'] = roc_auc_score(self.y_test,self.prop_test,'micro')
        
        # Plot ROC curves for the multilabel problem
        # ..........................................
        # Compute macro-average (metric for each label) ROC curve and ROC area
        # ref: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
        
        # First aggregate all false positive rates into 1d array
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))
    
        # Then interpolate for the tpr at all_fpr points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(n_classes):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])
    
        # Finally average it by n_classes and compute AUC
        mean_tpr /= n_classes
    
        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
    
        # This is the same as doing:
        roc_auc['macro'] = roc_auc_score(self.y_test,self.prop_test,'macro')
    
        # Plot all ROC curves
        plt.figure()
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.3f})'
                       ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)
        
        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.3f})'
                       ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)
    
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        lw = 1
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.3f})'
                     ''.format(i, roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC multi-class')
        plt.legend(loc="lower right")
        plt.show()
        
        test_results = {}
        test_results['accuracy'] = accuracy_score(self.y_test, 
                                                   self.pred_test)
        test_results['recall'] = recall_score(self.y_test, 
                                               self.pred_test,
                                               average='weighted')
        test_results['precision'] = precision_score(self.y_test, 
                                                     self.pred_test,
                                                     average='weighted')
        test_results['roc'] = roc_auc['macro']
        test_results['F1score'] = f1_score(self.y_test, 
                                                      self.pred_test, 
                                                      average='weighted') # weighted metric
        for metric in ['accuracy', 'recall', 'precision', 'roc', 'F1score']:
            print(f'\n{metric.capitalize()}\n' \
                  f'Test: {round(test_results[metric], 3)}')
        self.classification_report()

    def predict_train_test(self, model):
        # Assess performance of model
        self.start = time.time()
        self.pred_train = model.predict(self.X_train)
        self.prob_train = model.predict_proba(self.X_train)[:, 1]
        
        self.pred_test = model.predict(self.X_test)
        self.prob_test = model.predict_proba(self.X_test)[:, 1]
        
        self.accuracy_mean = model.score(self.X_test, self.y_test)
        print(f'Mean accuracy on test data and labels: {self.accuracy_mean:.3f}')
        self.time_taken = time.time() - self.start
        print(f"Time taken: {self.time_taken:.4f}s")
    
    def train_pred_eval_model(self, model, balanced=False):
        # train test evaluate individual classifier
        self.train_model(model, balanced)
        self.predict_train_test(model)
        self.classification_report()
        
    def pca(self, n_components=10):
        scaler = StandardScaler()
        scaled_df = scaler.fit_transform(self.df)
        pca = PCA(n_components = n_components)
        pca_vectors = pca.fit_transform(scaled_df)
        var_sum = 0
        for index, var in enumerate(pca.explained_variance_ratio_):
            var_sum += var
            print("Explained Variance ratio by Principal Component ", 
                  (index+1), " : ", var)
        print(f'Total variance explained = {var_sum}')
        
        print('Plotting principal components 1 and 2...')        
        plt.figure()
        sns.scatterplot(x=pca_vectors[:, 0], y=pca_vectors[:, 1], 
                        hue=self.labels)
        plt.title('Principal Components vs Class distribution', fontsize=16)
        plt.ylabel('Principal Component 2', fontsize=16)
        plt.xlabel('Principal Component 1', fontsize=16)
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        
    def evaluate_binary_model(self):
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
                
    def precision_recall_curve(self):
        # precision recall curve 
        precision, recall, _ = precision_recall_curve(self.y_test,self.prob_test)
        plt.figure(figsize = (8, 6))
        plt.rcParams['font.size'] = 16
        plt.plot(recall, precision, lw=2)
        plt.xlabel("recall")
        plt.ylabel("precision")
        plt.legend(loc="best")
        plt.title("precision vs. recall curve")
        plt.show()
    
    def roc_curve(self, model):
    # Calculate false positive rates and true positive rates
        base_fpr, base_tpr, _ = roc_curve(self.y_test, 
                                          [1 for _ in range(len(self.y_test))])
        model_fpr, model_tpr, _ = roc_curve(self.y_test, self.prob_test)
    
        #plt.figure(figsize = (8, 6))
        plt.rcParams['font.size'] = 16
        
        # Plot both curves
        if model == self.rf_model:
            label = f"RF (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.et_model:
            label = f"ET (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.gb_model:
            label = f"GB (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.xgb_model:
            label = f"XGB (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.knn_model:
            label = f"KNN (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.svm_model:
            label = f"SVM (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.lr_model:
            label = f"LR (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.lda_model:
            label = f"LDA (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.nb_model:
            label = f"NB (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.pipeline or model == self.ensemble_model:
            label = f"Ensemble (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        plt.plot(base_fpr, base_tpr, 'k--')#, label = 'baseline')
        plt.plot(model_fpr, model_tpr, 
                 label = label)
        plt.legend()
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves')        

    def precision_recall_vs_threshold(self):
        """
        Modified from:
        Hands-On Machine learning with Scikit-Learn
        and TensorFlow; p.89
        ***
        Note: this implementation is restricted to the binary classification task.
        ***
        """
        self.precisions, self.recalls, self.thresholds = precision_recall_curve(
            self.y_test, self.prob_test)
        plt.figure(figsize=(8, 8))
        plt.title("Precision and Recall Scores as a function of the decision threshold")
        plt.plot(self.thresholds, self.precisions[:-1], "b--", label="Precision")
        plt.plot(self.thresholds, self.recalls[:-1], "g-", label="Recall")
        plt.ylabel("Score")
        plt.xlabel("Decision Threshold")
        plt.legend(loc='best')
    
    def classification_report(self, target_names=None):
        print(classification_report(self.y_test, self.pred_test,
                                    target_names=target_names))
    
    def threshold_finder(self, required_fpr=None, required_tpr=None,
                         required_precision=None, required_recall=None):
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
        required_precision : float
            The required precision value. 
        required_recall : float
            The required recall value.     
        Returns
        -------
        array
            Threshold values corresponding to score < required_score.
    
        """
        # Threshold values for fpr tpr
        self.fpr, self.tpr, self.thresholds_fpr_tpr = roc_curve(
            self.y_test, self.prob_test)
        
        # Threshold values for precision recall
        self.precisions, self.recalls, self.thresholds_pre_rec = precision_recall_curve(
            self.y_test, self.prob_test)
        
        if required_fpr:
            self.threshold_required = self.thresholds_fpr_tpr[
                self.fpr < required_fpr]
        
        elif required_tpr:
            self.threshold_required = self.thresholds_fpr_tpr[
                self.tpr > required_tpr]
        
        elif required_precision:
            self.threshold_required = self.thresholds_pre_rec[
                self.precisions[:-1] >= required_precision]
        
        elif required_recall:
            self.threshold_required = self.thresholds_pre_rec[
                self.recalls[:-1] >= required_recall]
    
    def predict_with_new_threshold(self, required_fpr=None, required_tpr=None,
                                   required_precision=None, required_recall=None):
        # optimize for precision        
        self.threshold_finder(required_fpr, required_tpr, 
                              required_precision, required_recall)
        if required_fpr:   
            self.pred_test = (self.prob_test>self.threshold_required[-1]).astype(int)
        
        elif required_tpr:
            self.pred_test = (self.prob_test>self.threshold_required[0]).astype(int)
        
        elif required_precision:
            self.pred_test = (self.prob_test>self.threshold_required[0]).astype(int)
        
        elif required_recall:
            self.pred_test = (self.prob_test>self.threshold_required[-1]).astype(int)
        
    def confusion_matrix(self):
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
            
        plt.tight_layout()
        plt.ylabel('True label', size = 16)
        plt.xlabel('Predicted label', size = 16)
        plt.grid(None)
        
    def fi_model(self, model):
        # Feature importance from mean decrease in impurity
        self.fi_df = pd.DataFrame({'feature': self.features,
                   'importance': model.feature_importances_}).\
                    sort_values('importance', ascending = False)
        print(self.fi_df.head(10))
    
    def fi_permutation(self, model, test=True, train=False):
        # permutation importances
        fig, ax = plt.subplots()
        if test:
            result = permutation_importance(model, self.X_test, 
                                            self.y_test, n_repeats=10,
                                            random_state=42, n_jobs=2)
            sorted_idx = result.importances_mean.argsort()
            ax.boxplot(result.importances[sorted_idx].T,
                       vert=False, labels=self.X_test.columns[sorted_idx])
            ax.set_title("Permutation Importances (test set)")
        elif train: 
            result = permutation_importance(model, self.X_train, 
                                            self.y_train, n_repeats=10,
                                            random_state=42, n_jobs=2)
            sorted_idx = result.importances_mean.argsort()
            ax.boxplot(result.importances[sorted_idx].T,
                       vert=False, labels=self.X_train.columns[sorted_idx])
            ax.set_title("Permutation Importances (train set)")
        fig.tight_layout()
        plt.show()
        
    def plot_fi_model(self):
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
        
    def grid_search_wrapper(self,clf,params,scorers,
                            k = 3, refit_score='precision_score',
                            randomized=True):
        """
        fits a GridSearchCV or RandomizedSearchCV classifier using 
        refit_score for optimization.
        prints classifier performance metrics:
        
        """
        skf = StratifiedKFold(n_splits=k)
        if randomized:
            self.search = RandomizedSearchCV(clf, 
                                param_distributions=params,
                                scoring=scorers,
                                refit=refit_score,
                                random_state=42, 
                                n_iter=10, 
                                cv=skf, 
                                verbose=1,
                                return_train_score=True,
                                n_jobs=-1)
        else:
            self.search = GridSearchCV(clf, params, scoring=scorers,
                                   refit=refit_score, cv=skf, 
                                   return_train_score=True, n_jobs=-1)
        
        self.search.fit(self.X_train, self.y_train)
    
        # make the predictions
        self.pred_test = self.search.predict(self.X_test)
        self.prob_test = self.search.predict_proba(self.X_test)
        
        print('Model with rank: 1')
        self.print_grid_search_result()
        print(f'Best params for {refit_score}')
        print(self.search.best_params_)
    
        # confusion matrix on the test data.
        print('\nConfusion matrix of Random Forest optimized for {} on the test data:'.format(refit_score))
        print(pd.crosstab(self.y_test, self.pred_test, rownames=['True'],
                       colnames=['Predicted']))
        
        # for binary classifier
        # print(pd.DataFrame(confusion_matrix(self.y_test, y_pred),
        #              columns=['pred_neg', 'pred_pos'], index=['neg', 'pos']))
    
    def print_grid_search_result(self):
        self.search_results = pd.DataFrame(self.search.cv_results_)
        self.search_results = self.search_results.sort_values(
                                        by='mean_test_precision_score', 
                                        ascending=False)
        print(self.search_results[['mean_test_precision_score',
                                   'std_test_precision_score',
                                   'mean_test_recall_score',
                                   'std_test_recall_score',
                                   'mean_test_accuracy_score',
                               'std_test_accuracy_score']].round(3).head(1))
        
        
    def save_model(self, model):
        # pickle the model for future use
        classifier_pkl = open('rf_classifier.pkl','wb')
        pickle.dump(model, classifier_pkl)
        classifier_pkl.close()
        print('Pickling complete.')

# In[]:

if __name__ == '__main__':
        
    # dataset 
    csv_file = '../../Datasets/user_classification/ind_vs_bot/datasets_all/user_features_labels_noNan.csv'
    csv_file = '../../Datasets/user_classification/ind_vs_org/datasets_all/user_features_labels_noNan.csv'
    csv_file = '../../Datasets/user_classification/ground_truth/features_labels/human_bot_org_features_labels_noNan.csv'
    
    # instantiate classifier class
    m1 = BuildClassifier(csv_file)
    
    # plot class distribution in raw dataset
    m1.class_distribution()
    
    # split dataset
    m1.split_train_test()
    
    # feature scaling
    m1.feature_scaling()
    
    # balance train dataset
    m1.resample('up')
    
    # classifiers
    m1.pipeline_lr = Pipeline(steps=[('scaler',StandardScaler()),
                             ('classifier', LogisticRegression(
                                 multi_class='multinomial',
                                 solver='saga',
                                 max_iter=200))])
    
    
    m1.pipeline_lr_pca = Pipeline(steps=[('scaler',StandardScaler()),
                             ('pca', PCA(n_components = 10)),
                             ('classifier', LogisticRegression(
                                 multi_class='multinomial', 
                                 solver='saga', 
                                 max_iter=200))])

    m1.pipeline_svm = Pipeline(steps=[('scaler',StandardScaler()),
                                 ('classifier', SVC(probability=True,
                                                    break_ties=True))])

    m1.pipeline_mlp = Pipeline(steps=[('scaler',StandardScaler()),
                             ('classifier', MLPClassifier(hidden_layer_sizes=(
                                 int(m1.df.columns.shape[0]/2), 
                                 int(m1.df.columns.shape[0]/2/2))))])
    
    m1.pipeline_knn = Pipeline(steps=[('scaler',StandardScaler()),
                                 ('classifier', m1.knn_model)])
    
    m1.pipeline_ensemble = Pipeline([('scaler', StandardScaler()), 
                             ('classifier', m1.ensemble_model)])
    
    m1.ovr_xgb = OneVsRestClassifier(m1.xgb_model)
    
    classifiers = [m1.rf_model, 
                   m1.gb_model, 
                   m1.xgb_model, 
                   m1.et_model,
                   m1.knn_model, 
                   m1.svm_model,
                   m1.lr_model,
                   m1.lda_model,
                   m1.nb_model,
                   m1.pipeline_ensemble]
    
    # train model (using original train test split)
    for clf in classifiers:
        m1.train_model(clf)
    
    # train model (with oversampling using SMOTE)
    for clf in classifiers:
        m1.train_model(clf, balanced=True)
    
    # predict with trained model
    for clf in classifiers:
        m1.predict_train_test(clf)
        m1.roc_curve(clf)

    # evaluate performance of trained model using roc curve
    for clf in classifiers:
        m1.evaluate_binary_model(clf)
    plt.legend()
    #plt.savefig('ROC_curve_rf_smote.png')
    #plt.close()
    
    # classification report
    m1.classification_report()
    
    # evaluate confusion matrix
    m1.confusion_matrix()
    m1.plot_confusion_matrix(classes = ['Individual', 'Bot'],
                              title = 'User Confusion Matrix')
    #plt.savefig('Confusion_matrix_rf_smote.png')
    #plt.close()
    
    # validate model using k_fold cross validation
    for clf in classifiers:
        m1.k_fold_cv(clf)

    for clf in classifiers:
        m1.k_fold_cv(clf, balanced=True)
        
    # feature importance 
    m1.fi_model(m1.rf_model)
    m1.plot_fi_model()
    
    ###################### FINE TUNNING MODEL #########################
    # change threshold
    m1.predict_with_new_threshold(required_fpr=0.05)
    m1.confusion_matrix()
    
    # Fine-tune model decision threshold based on precision and recall  
    m1.precision_recall_curve()
    m1.plot_precision_recall_vs_threshold(m1.precision, m1.recall, 
                                          m1.thresholds)
    
    # Hyperparam tuning- grid search method based on a score (e.g. precision)
    #rf_model params
    params = {
        'min_samples_split': [3, 5, 10], 
        'n_estimators' : [100, 300],
        'max_depth': [3, 5, 15, 25],
        'max_features': [3, 5, 10, 20]
    }
    
    # xgb_model params
    params = {
    # uniform distribution from 0.7 to 1 (0.3+0.7)
    "colsample_bytree": uniform(0.7, 0.3),
    "gamma": uniform(0, 0.5),
    "learning_rate": uniform(0.03, 0.3), # default 0.1 
    "max_depth": randint(3, 15), # default 3
    "n_estimators": randint(100, 150), # default 100
    "min_child_weight" : randint(1, 7),
    "subsample": uniform(0.6, 0.4)
    }
    
    scorers = {
        'precision_score': make_scorer(precision_score, average='binary'), 
        'recall_score': make_scorer(recall_score, average='binary'),
        'accuracy_score': make_scorer(accuracy_score)
    }
    
    m1.grid_search_wrapper(m1.xgb_model,
                            params,
                            scorers,
                            refit_score='precision_score')
        
    # predict with the fine-tunned best_estimator
    m1.predict_train_test(m1.search.best_estimator_)

    # revaluate performance
    m1.evaluate_binary_model(m1.search.best_estimator_) # this is pretty stupid, the hyperparam tunning made the model perform worst on the test set.
    
    ## Plot learning curve to spot overfitting
    # binary
    m1.xgb_model = XGBClassifier(objective="binary:logistic", 
                                     random_state=42, 
                                     eval_metric=['error','logloss'])
    # multiclass
    m1.xgb_model = XGBClassifier(objective="multi:softprob", 
                                     random_state=42, 
                                     eval_metric=['merror','mlogloss'])
    
    m1.xgb_model.fit(m1.X_train, m1.y_train, 
                     eval_set=[(m1.X_train,m1.y_train),(m1.X_test,m1.y_test)],
                     verbose=True)
    
    # retrieve performance metrics
    results = m1.xgb_model.evals_result()
    epochs = len(results['validation_0']['merror'])
    x_axis = range(0, epochs)
    # plot log loss
    fig, ax = plt.subplots()
    ax.plot(x_axis, results['validation_0']['mlogloss'], label='Train')
    ax.plot(x_axis, results['validation_1']['mlogloss'], label='Test')
    ax.legend()
    plt.ylabel('Log Loss')
    plt.title('XGBoost Log Loss')
    plt.show()
    # plot classification error
    fig, ax = plt.subplots()
    ax.plot(x_axis, results['validation_0']['merror'], label='Train')
    ax.plot(x_axis, results['validation_1']['merror'], label='Test')
    ax.legend()
    plt.ylabel('Classification Error')
    plt.title('XGBoost Classification Error')
    plt.show()

    # implement early stopping to find optimal number of boosting rounds
    # if more than one evaluation metric are given the last one is used for early stopping
    m1.xgb_model.fit(m1.X_train, m1.y_train, 
                     early_stopping_rounds=10, 
                     eval_set=[(m1.X_test,m1.y_test)],
                     eval_metric="mlogloss",
                     verbose=True)
    
    print(f"best score: {m1.xgb_model.best_score},"
        f" best iteration: {m1.xgb_model.best_iteration},"
        f" best ntree limit {m1.xgb_model.best_ntree_limit}") 
    
    m1.predict_train_test(m1.xgb_model)
    m1.precision_recall_fscore_support()
    m1.evaluate_binary_model(m1.xgb_model)
    
    # xgb_model feature importance
    plot_importance(m1.xgb_model)
    
    # plot the output tree via matplotlib, specifying the ordinal number of the target tree
    plot_tree(m1.xgb_model, num_trees=m1.xgb_model.best_iteration)
    
    ############################# SAVE MODEL #############################
    m1.save_model(m1.rf_model)
    
    print('\n _______________ Testing on another dataset ________________')
    # df = pd.read_csv('../Datasets/user_classification/ind_vs_bot/dataset1/user_features_labels_noNan_dropped_fav_retweet_cols.csv', index_col=0)
    # labels = np.array(df1.pop('labels'))
    # rf_pred = m1.rf_model.predict(df1)
    # cm = confusion_matrix(labels, rf_pred)
    # print(cm)
    
    # In[]:
    
    # multiclass classifier
    
    csv_file = '../../Datasets/user_classification/ground_truth/features_labels/human_bot_org_features_labels_noNan.csv'
    
    # instantiate class
    m1 = BuildClassifier(csv_file)
    
    # binarize outputs into one-hot encoding format (for OneVsRestClassifier)
    m1.binarize_output()
    n_classes = m1.labels.shape[1]
    
    # split training and test sets
    m1.split_train_test()
    
    # balance train dataset
    m1.resample()
    
    m1.train_predict_evaluate_OneVsRestClassifier(m1.xgb_model)
    
    ########## multiclass classification confusion matrix ####################
    # print(pd.crosstab(m1.y_test, m1.pred_test, rownames=['True'],
    #                   colnames=['Predicted']))
    
    # fine-tunning rf- method 1: grid search for maximising a score 
    param_grid_rf = {
        'min_samples_split': [3, 5, 10], 
        'n_estimators' : [100, 300],
        'max_depth': [3, 5, 15, 25],
        'max_features': [3, 5, 10, 20]
    }
    
    param_grid_gb = {
    "loss":["deviance"],
    "learning_rate": [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2],
    "min_samples_split": np.linspace(0.1, 0.5, 12),
    "min_samples_leaf": np.linspace(0.1, 0.5, 12),
    "max_depth":[15,20,25,30],
    "max_features":["log2","sqrt"],
    "criterion": ["friedman_mse",  "mae"],
    "subsample":[0.5, 0.618, 0.8, 0.85, 0.9, 0.95, 1.0],
    "n_estimators":[100,200]
    }

    scorers = {
        'precision_score': make_scorer(precision_score, average='weighted'), 
        'recall_score': make_scorer(recall_score, average='weighted'),
        'accuracy_score': make_scorer(accuracy_score)
    }
    
    
    m1.grid_search_wrapper(m1.gb_model,
                            param_grid_gb,
                            scorers,
                            refit_score='precision_score')
    
    
    ##########################################################################
