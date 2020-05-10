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
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, cross_val_score, ShuffleSplit, learning_curve
from sklearn.preprocessing import StandardScaler, label_binarize, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve, auc
from sklearn.metrics import f1_score, recall_score, precision_score, make_scorer, accuracy_score, roc_auc_score
from sklearn.metrics import precision_recall_fscore_support, classification_report
from sklearn.metrics import multilabel_confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier
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
from imblearn.combine import SMOTEENN
from sklearn.utils import resample
from sklearn.utils.class_weight import compute_class_weight
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
                                               bootstrap=True,
                                               criterion='gini',
                                               random_state=self.RSEED,
                                               max_features='sqrt',
                                               n_jobs=-1,
                                               verbose=1,
                                               class_weight="balanced")
        self.et_model = ExtraTreesClassifier(n_estimators=500,
                                             n_jobs=-1,
                                             random_state=self.RSEED)
        self.gb_model = GradientBoostingClassifier(n_estimators=100,
                                                   random_state=self.RSEED)
        self.xgb_model = XGBClassifier(n_estimators=100,
                                       random_state=self.RSEED)
        self.adab_model = AdaBoostClassifier(self.rf_model)
        self.knn_model = KNeighborsClassifier(n_neighbors=5)
        self.svm_model = SVC(gamma='auto', probability=True)
        self.lr_model = LogisticRegression(random_state=42)
        self.lda_model = LinearDiscriminantAnalysis()
        self.nb_model = GaussianNB()
        # 2 hidden layers, first layer is half the size of the feature space
        self.mlp_model = MLPClassifier(hidden_layer_sizes=(
            int(self.df.columns.shape[0] / 2),
            int(self.df.columns.shape[0] / 2 / 2)))
        self.ensemble_model = VotingClassifier(
            estimators=[('lr', self.lr_model),
                        ('svm', self.svm_model),
                        ('rf', self.rf_model),
                        ('adab', self.adab_model),
                        ('xgb', self.xgb_model)], voting='soft')

    def class_distribution(self):
        plt.figure()
        sns.countplot(x=self.labels, color='black')
        plt.title('Class distribution', fontsize=16)
        plt.ylabel('Class Counts', fontsize=16)
        plt.xlabel('Class Label', fontsize=16)
        plt.xticks(rotation='vertical')
        for p in plt.gca().patches:
            plt.gca().annotate('{:.0f}'.format(p.get_height()),
                               (p.get_x() + 0.25, p.get_height() + 50))
        plt.tight_layout()

    def binarize_output(self):
        self.labels = label_binarize(self.labels,
                                     classes=list(
                                         np.unique(self.labels).astype(int)))

    def split_train_test(self, test_size=0.2):
        print('\n Split Data into Training and Testing Set...')
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.labels, stratify=self.labels,
            test_size=test_size, random_state=self.RSEED)  # stratify means train and test sample have same proportions of each class
        print(f'Train data shape: {self.X_train.shape}')
        if np.ndim(self.labels) == 1:
            print(
                f'Train class distribution:\n{pd.Series(self.y_train).value_counts(normalize=True)}')
        print(f'Test data shape: {self.X_test.shape}')
        if np.ndim(self.labels) == 1:
            print(
                f'Test class distribution:\n{pd.Series(self.y_test).value_counts(normalize=True)}')
        print('\n ...Splitting complete!')

    def sample_weight(self):
        self.sample_weights = np.ones(self.y_train.shape[0], dtype='float')
        self.class_weights = list(compute_class_weight('balanced',
                                                       np.unique(self.y_train),
                                                       self.y_train))
        for i, val in enumerate(self.y_train):
            self.sample_weights[i] = self.class_weights[val]

    def resample(self, method='smote'):
        """

        Parameters
        ----------
        method : string, optional
            Resampling methods: 'smote', 'smoteenn' 'up', 'down'.
            The default is 'smote'.
            This is to be used after split_train_test() method.
        Returns
        -------
        None.

        """
        if method == 'smote':
            # Balance training data to have equal numbers of each class
            sm = SMOTE(random_state=42)
            self.X_train_balanced, self.y_train_balanced = sm.fit_resample(
                self.X_train, self.y_train)
        elif method == 'smoteenn':
            # over-sampling using SMOTE and cleaning using ENN
            sme = SMOTEENN(random_state=42)
            self.X_train_balanced, self.y_train_balanced = sme.fit_resample(
                self.X_train, self.y_train)
        elif method == 'up':
            # recombine training features and labels into a single df
            self.train_df = self.X_train.copy()
            self.train_df['labels'] = self.y_train

            # majority class
            self.train_df0 = self.train_df[self.train_df.labels == 0]
            n_samples_maj = max(self.train_df.labels.value_counts())

            # upsample minority classes
            self.train_df1 = resample(self.train_df[self.train_df.labels == 1],
                                      replace=True,             # sample with replacement
                                      n_samples=n_samples_maj,  # to match majority class
                                      random_state=42)
            if 2 in self.train_df.labels.values:
                self.train_df2 = resample(self.train_df[self.train_df.labels == 2],
                                          replace=True,             # sample with replacement
                                          n_samples=n_samples_maj,  # to match majority class
                                          random_state=42)

                # Combine majority class with upsampled minority class
                self.train_df_balanced = pd.concat([self.train_df0,
                                                    self.train_df1,
                                                    self.train_df2])
            else:
                # Combine majority class with upsampled minority class
                self.train_df_balanced = pd.concat([self.train_df0,
                                                    self.train_df1])
            self.y_train_balanced = np.array(self.train_df_balanced.labels)
            self.X_train_balanced = self.train_df_balanced.loc[:,
                                                               self.train_df_balanced.columns != 'labels']

        elif method == 'down':
            # recombine training features and labels into a single df
            self.train_df = self.X_train.copy()
            self.train_df['labels'] = self.y_train

            # minority class
            self.train_df0 = self.train_df[self.train_df.labels == 1]
            n_samples_min = min(self.train_df.labels.value_counts())
            n_samples_min = 5000

            # upsample minority classes
            self.train_df1 = resample(self.train_df[self.train_df.labels == 0],
                                      replace=False,             # sample with replacement
                                      n_samples=n_samples_min,  # to match majority class
                                      random_state=42)

            if 2 in self.train_df.labels.values:
                self.train_df2 = resample(self.train_df[self.train_df.labels == 2],
                                          replace=False,             # sample with replacement
                                          n_samples=n_samples_min,  # to match majority class
                                          random_state=42)

                # Combine minority class with downsampled majority class
                self.train_df_balanced = pd.concat([self.train_df0,
                                                    self.train_df1,
                                                    self.train_df2])
            else:
                # Combine minority class with downsampled majority class
                self.train_df_balanced = pd.concat([self.train_df0,
                                                    self.train_df1])
            self.y_train_balanced = np.array(self.train_df_balanced.labels)
            self.X_train_balanced = self.train_df_balanced.loc[:,
                                                               self.train_df_balanced.columns != 'labels']

        if np.ndim(self.labels) == 1:
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
        if len(np.unique(self.labels)) != 2:
            # binary classification
            f1_scoring = 'f1_weighted'
            pre_scoring = 'precision_weighted'
            rec_scoring = 'recall_weighted'
        else:
            # binary classification
            f1_scoring = 'f1'
            pre_scoring = 'precision'
            rec_scoring = 'recall'

        if balanced:
            self.f1scores_cv = cross_val_score(model,
                                               self.X_train_balanced,
                                               self.y_train_balanced,
                                               cv=k,
                                               scoring=f1_scoring)
            self.precision_cv = cross_val_score(model,
                                                self.X_train_balanced,
                                                self.y_train_balanced,
                                                cv=k,
                                                scoring=pre_scoring)
            self.recall_cv = cross_val_score(model,
                                             self.X_train_balanced,
                                             self.y_train_balanced,
                                             cv=k,
                                             scoring=rec_scoring)
        else:
            self.f1scores_cv = cross_val_score(model,
                                               self.X_train,
                                               self.y_train,
                                               cv=k,
                                               scoring=f1_scoring)
            self.precision_cv = cross_val_score(model,
                                                self.X_train,
                                                self.y_train,
                                                cv=k,
                                                scoring=pre_scoring)
            self.recall_cv = cross_val_score(model,
                                             self.X_train,
                                             self.y_train,
                                             cv=k,
                                             scoring=rec_scoring)

        print(f'Mean F1 score: {self.f1scores_cv.mean():.4f} +- '
              f'{self.f1scores_cv.std():.4f}')
        print(f'Mean precision: {self.precision_cv.mean():.4f} +- '
              f'{self.precision_cv.std():.4f}')
        print(f'Mean recall: {self.recall_cv.mean():.4f} +- '
              f'{self.recall_cv.std():.4f}')
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

    def train_model(self, model, balanced=False):
        # Fit model on training data
        self.start = time.time()
        if balanced:
            model.fit(self.X_train_balanced, self.y_train_balanced)
        else:
            if type(model) == Pipeline:
                try:
                    model.fit(self.X_train, self.y_train,
                              classifier__sample_weight=self.sample_weights)
                except TypeError:
                    model.fit(self.X_train, self.y_train)
            # elif type(model) == OneVsRestClassifier:
            #     model.fit(self.X_train, self.y_train)
            else:
                try:
                    model.fit(self.X_train, self.y_train, self.sample_weights)
                except TypeError:
                    model.fit(self.X_train, self.y_train)
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

    def train_predict_evaluate_OneVsRestClassifier(self, estimator,
                                                   balanced=False):
        # Learn to predict each class against the other
        random_state = np.random.RandomState(0)
        self.OVRClassifier = OneVsRestClassifier(estimator)
        if balanced:
            self.OVRClassifier.fit(
                self.X_train_balanced,
                self.y_train_balanced)
        else:
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
            fpr[i], tpr[i], _ = roc_curve(
                self.y_test[:, i], self.prop_test[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
            # This is the same as doing:
            roc_auc[i] = roc_auc_score(
                self.y_test[:, i], self.prop_test[:, i], 'macro')  # roc_auc for ith class

            # precision-recall
            precision[i], recall[i], _ = precision_recall_curve(
                self.y_test[:, i], self.prop_test[:, i])
            plt.plot(recall[i], precision[i], lw=2, label='class {}'.format(i))

        # precision recall curve
        plt.xlabel("recall")
        plt.ylabel("precision")
        plt.legend(loc="best")
        plt.title("precision vs. recall curve")
        plt.show()

        # Compute micro-average ((global metric) ROC curve and ROC area
        # ref:
        # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
        fpr["micro"], tpr["micro"], _ = roc_curve(
            self.y_test.ravel(), self.prop_test.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # This is the same as doing:
        roc_auc['micro'] = roc_auc_score(self.y_test, self.prop_test, 'micro')

        # Plot ROC curves for the multilabel problem
        # ..........................................
        # Compute macro-average (metric for each label) ROC curve and ROC area
        # ref:
        # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html

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
        roc_auc['macro'] = roc_auc_score(self.y_test, self.prop_test, 'macro')

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
        test_results['F1score'] = f1_score(
            self.y_test, self.pred_test, average='weighted')  # weighted metric
        for metric in ['accuracy', 'recall', 'precision', 'roc', 'F1score']:
            print(f'\n{metric.capitalize()}\n'
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
        print(
            f'Mean accuracy on test data and labels: {self.accuracy_mean:.3f}')
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
        pca = PCA(n_components=n_components)
        pca_vectors = pca.fit_transform(scaled_df)
        var_sum = 0
        for index, var in enumerate(pca.explained_variance_ratio_):
            var_sum += var
            print("Explained Variance ratio by Principal Component ",
                  (index + 1), " : ", var)
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
        baseline['accuracy'] = accuracy_score(self.y_test, [1 for _ in range(
            len(self.y_test))])  # always predict the majority class
        baseline['recall'] = recall_score(
            self.y_test, [1 for _ in range(len(self.y_test))])  # always predict positive
        baseline['precision'] = precision_score(
            self.y_test, [1 for _ in range(len(self.y_test))])  # always predict positive
        baseline['roc'] = 0.5
        baseline['F1score'] = 2 * 0.5 / (0.5 + 1)

        test_results = {}
        test_results['accuracy'] = accuracy_score(self.y_test, self.pred_test)
        test_results['recall'] = recall_score(self.y_test, self.pred_test)
        test_results['precision'] = precision_score(
            self.y_test, self.pred_test)
        test_results['roc'] = roc_auc_score(self.y_test, self.prob_test)
        test_results['F1score'] = f1_score(
            self.y_test, self.pred_test)  # binary classifier

        train_results = {}
        train_results['accuracy'] = accuracy_score(
            self.y_train, self.pred_train)
        train_results['recall'] = recall_score(self.y_train, self.pred_train)
        train_results['precision'] = precision_score(
            self.y_train, self.pred_train)
        train_results['roc'] = roc_auc_score(self.y_train, self.prob_train)
        train_results['F1score'] = f1_score(self.y_train, self.pred_train)

        for metric in ['accuracy', 'recall', 'precision', 'roc', 'F1score']:
            print(f'\n{metric.capitalize()}\n'
                  f'Baseline: {round(baseline[metric], 3)} | '
                  f'Test: {round(test_results[metric], 3)} | '
                  f'Train: {round(train_results[metric], 3)} ')

    def precision_recall_curve(self):
        # precision recall curve
        precision, recall, _ = precision_recall_curve(
            self.y_test, self.prob_test)
        plt.figure(figsize=(8, 6))
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
        elif model == self.adab_model:
            label = f"AdaB (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.knn_model:
            label = f"KNN (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.lda_model:
            label = f"LDA (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif model == self.nb_model:
            label = f"NB (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
        elif type(model) == Pipeline:
            if model['classifier'] == self.svm_model:
                label = f"SVM (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
            elif model['classifier'] == self.lr_model:
                label = f"LR (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
            elif model['classifier'] == self.mlp_model:
                label = f"MLP (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"
            elif model['classifier'] == self.ensemble_model:
                label = f"Ensemble (AUC = {roc_auc_score(self.y_test, self.prob_test):.3f})"

        plt.plot(base_fpr, base_tpr, 'k--')  # , label = 'baseline')
        plt.plot(model_fpr, model_tpr,
                 label=label)
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
        plt.title(
            "Precision and Recall Scores as a function of the decision threshold")
        plt.plot(self.thresholds,
                 self.precisions[:-1],
                 "b--",
                 label="Precision")
        plt.plot(self.thresholds, self.recalls[:-1], "g-", label="Recall")
        plt.ylabel("Score")
        plt.xlabel("Decision Threshold")
        plt.legend(loc='best')

    def classification_report(self, target_names=None):
        print(classification_report(self.y_test, self.pred_test,
                                    target_names=target_names, digits=3))

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

    def predict_with_new_threshold(
            self,
            required_fpr=None,
            required_tpr=None,
            required_precision=None,
            required_recall=None):
        # optimize for precision
        self.threshold_finder(required_fpr, required_tpr,
                              required_precision, required_recall)
        if required_fpr:
            self.pred_test = (
                self.prob_test > self.threshold_required[-1]).astype(int)

        elif required_tpr:
            self.pred_test = (
                self.prob_test > self.threshold_required[0]).astype(int)

        elif required_precision:
            self.pred_test = (
                self.prob_test > self.threshold_required[0]).astype(int)

        elif required_recall:
            self.pred_test = (
                self.prob_test > self.threshold_required[-1]).astype(int)

    def confusion_matrix(self):
        # calculate confusion matrix
        self.cm = confusion_matrix(self.y_test, self.pred_test)
        print(self.cm)
        TPR = self.cm[1][1] / (sum(self.cm[1]))
        TNR = self.cm[0][0] / (sum(self.cm[0]))
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
            self.cm = self.cm.astype('float') / \
                self.cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')

        print(self.cm)

        plt.figure(figsize=(10, 8))
        plt.imshow(self.cm, interpolation='nearest', cmap=cmap)
        plt.title(title, size=16)
        plt.colorbar(aspect=4)
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45, size=14)
        plt.yticks(tick_marks, classes, size=14)

        fmt = '.2f' if normalize else 'd'
        thresh = self.cm.max() / 2.

        # Labeling the plot
        for i, j in itertools.product(
            range(
                self.cm.shape[0]), range(
                self.cm.shape[1])):
            plt.text(j, i, format(self.cm[i, j], fmt), fontsize=20,
                     horizontalalignment="center",
                     color="white" if self.cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.ylabel('True label', size=16)
        plt.xlabel('Predicted label', size=16)
        plt.grid(None)

    def fi_model(self, model):
        # Feature importance from mean decrease in impurity
        self.fi_df = pd.DataFrame({'feature': self.features,
                                   'importance': model.feature_importances_}).\
            sort_values('importance', ascending=False)
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
        plt.bar(x_values, importances, orientation='vertical', color='r',
                edgecolor='k', linewidth=1.2)

        # Tick labels for x axis
        plt.xticks(x_values, self.fi_df.feature, rotation='vertical')

        # Axis labels and title
        plt.ylabel('Importance')
        plt.xlabel('Variable')
        plt.title('Variable Importances')

        # List of features sorted from most to least important
        sorted_importances = self.fi_df.importance
        sorted_features = self.fi_df.feature

        # Cumulative importances
        cumulative_importances = np.cumsum(sorted_importances)

        # Make a line graph
        plt.plot(x_values, cumulative_importances, 'g-')

        # Draw line at 95% of importance retained
        plt.hlines(y=0.95, xmin=0, xmax=len(sorted_importances),
                   color='r', linestyles='dashed')

        # Format x ticks and labels
        plt.xticks(x_values, sorted_features, rotation='vertical')

        # Axis labels and title
        plt.xlabel('Variable')
        plt.ylabel('Cumulative Importance')
        plt.title('Cumulative Importances')
        plt.tight_layout()
        # plt.grid(True)

    def feature_distribution(self, feature, hist=True, kde=True,
                             norm_hist=True, bins=100):
        """
        Plot the distribution of a feature grouped by labels.

        feature: str
        feature name
        """
        unique_labels = np.sort(np.unique(self.df.labels.to_numpy()))
        for label in unique_labels:
            df_feature = self.df[self.df.labels == label]
            sns.distplot(df_feature[feature],
                         bins=bins,
                         hist=hist,
                         kde=kde,
                         norm_hist=norm_hist,
                         label=f'{label}')

    def grid_search_wrapper(self, clf, params, scorers,
                            k=3, refit_score='precision_score',
                            randomized=True, n_iter=10):
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
                                             n_iter=n_iter,
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
        print(
            f'\nConfusion matrix of {str(clf.__class__)} optimized for {refit_score} on the test data:')
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
        pickle.dump(model, open("model_pkl.dat", "wb"))
        print('Pickling complete.')

    def load_model(self, model_pkl_file):
        return pickle.load(open(model_pkl_file, "rb"))

# In[]:


if __name__ == '__main__':

    # dataset
    csv_file = 'ground_truth_datasets/feature_matrix/human_bot_org_features_labels_noNan_new.csv'

    # instantiate classifier class
    m1 = BuildClassifier(csv_file)

    # Considering a subset of features:
    # --------------------- account-related features--------------------------
    m1.df = m1.df[['nFollowers',
                   'nFollowings',
                   'FollowersToFollowing',
                   'nLists',
                   'nFavs',
                   'nPosts',
                   'geo',
                   'location',
                   'url',
                   'description',
                   'verified',
                   'fav_tweets',
                   'fav_retweets',
                   'fav_replies',
                   'ret_tweets',
                   'ret_retweets',
                   'ret_replies',
                   'pop_fav_tweets',
                   'pop_fav_retweets',
                   'pop_fav_replies',
                   'pop_ret_tweets',
                   'pop_ret_retweets',
                   'pop_ret_replies',
                   'nPostMention',
                   'nPostQuote',
                   'nPostPlace',
                   'age',
                   'screen_name_len',
                   'levenshtein_name_screen_name',
                   'labels']]
    # ------------------------ tweet-behavioral -------------------------------
    m1.df = m1.df[['Tavg', 'Tavg_tweet', 'Tavg_ret', 'Tavg_quote',
                   'Tavg_reply', 'labels']]

    m1.X = m1.df.loc[:, m1.df.columns != 'labels']
    m1.features = list(m1.X)

    # plot class distribution in raw dataset
    m1.class_distribution()

    # split dataset
    m1.split_train_test()

    # get sample weights
    m1.sample_weight()

    # balance train dataset
    m1.resample()

    # classifiers
    m1.pipeline_lr = Pipeline(steps=[('scaler', StandardScaler()),
                                     ('classifier', m1.lr_model)])

    m1.pipeline_lr_pca = Pipeline(steps=[('scaler', StandardScaler()),
                                         ('pca', PCA(n_components=10)),
                                         ('classifier', LogisticRegression(
                                             multi_class='multinomial',
                                             solver='saga',
                                             max_iter=200))])

    m1.pipeline_svm = Pipeline(steps=[('scaler', StandardScaler()),
                                      ('classifier', m1.svm_model)])

    m1.pipeline_mlp = Pipeline(steps=[('scaler', StandardScaler()),
                                      ('classifier', m1.mlp_model)])

    m1.pipeline_ensemble = Pipeline([('scaler', StandardScaler()),
                                     ('classifier', m1.ensemble_model)])

    m1.ovr_xgb = OneVsRestClassifier(m1.xgb_model)
    m1.ovr_adab = OneVsRestClassifier(m1.adab_model)

    classifiers = [m1.nb_model,
                   m1.pipeline_svm,
                   m1.pipeline_lr,
                   m1.pipeline_mlp,
                   m1.rf_model,
                   m1.gb_model,
                   m1.xgb_model,
                   m1.et_model,
                   m1.adab_model,
                   # m1.pipeline_ensemble,
                   ]

    # train model (using original train test split)
    for clf in classifiers:
        print(clf)
        m1.train_model(clf)

    # train model (with oversampling using SMOTE)
    for clf in classifiers:
        m1.train_model(clf, balanced=True)

    # predict with trained model
    for clf in classifiers:
        print(clf)
        m1.predict_train_test(clf)
        m1.roc_curve(clf)
        # m1.evaluate_binary_model()

    plt.legend()
    # plt.savefig('ROC_curve_rf_smote.png')
    # plt.close()

    # classification report
    m1.classification_report()

    # evaluate confusion matrix
    m1.confusion_matrix()
    m1.plot_confusion_matrix(classes=['Individual', 'Bot', 'Org'],
                             title='User Confusion Matrix')
    # plt.savefig('Confusion_matrix_rf_smote.png')
    # plt.close()

    # validate model using k_fold cross validation
    for clf in classifiers[4:]:
        print(clf)
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
    # rf_model params
    params = {
        'min_samples_split': [3, 5, 10],
        'n_estimators': [100, 300],
        'max_depth': [3, 5, 15, 25],
        'max_features': [3, 5, 10, 20]
    }

    # xgb_model params
    params = {
        # uniform distribution from 0.7 to 1 (0.3+0.7)
        "colsample_bytree": uniform(0.7, 0.3),
        "gamma": uniform(0, 0.5),
        "learning_rate": uniform(0.03, 0.3),  # default 0.1
        "max_depth": randint(3, 15),  # default 3
        "n_estimators": randint(100, 150),  # default 100
        "min_child_weight": randint(1, 7),
        "subsample": uniform(0.6, 0.4)
    }

    scorers = {
        'precision_score': make_scorer(
            precision_score,
            average='weighted'),
        'recall_score': make_scorer(
            recall_score,
            average='weighted'),
        'accuracy_score': make_scorer(accuracy_score),
        'roc_auc_score': make_scorer(
            roc_auc_score,
            average='macro',
            multi_class='ovr'),
        'f1_score': make_scorer(
            f1_score,
            average='weighted')}

    m1.grid_search_wrapper(m1.ovr_xgb,
                           params,
                           scorers,
                           refit_score='f1_score',
                           n_iter=5)

    # predict with the fine-tunned best_estimator
    m1.predict_train_test(m1.search.best_estimator_)

    # revaluate performance
    # this is pretty stupid, the hyperparam tunning made the model perform
    # worst on the test set.
    m1.evaluate_binary_model()

    # Plot learning curve to spot overfitting
    # binary
    m1.xgb_model = XGBClassifier(objective="binary:logistic",
                                 random_state=42,
                                 eval_metric=['error', 'logloss'])
    # multiclass
    m1.xgb_model = XGBClassifier(objective="multi:softprob",
                                 random_state=42,
                                 eval_metric=['merror', 'mlogloss'])

    m1.xgb_model.fit(
        m1.X_train, m1.y_train, eval_set=[
            (m1.X_train, m1.y_train), (m1.X_test, m1.y_test)], verbose=True)

    # retrieve performance metrics
    results = m1.xgb_model.evals_result()
    epochs = len(results['validation_0']['error'])
    x_axis = range(0, epochs)
    # plot log loss
    fig, ax = plt.subplots()
    ax.plot(x_axis, results['validation_0']['logloss'], label='Train')
    ax.plot(x_axis, results['validation_1']['logloss'], label='Test')
    ax.legend()
    plt.ylabel('Log Loss')
    plt.title('XGBoost Log Loss')
    plt.show()
    # plot classification error
    fig, ax = plt.subplots()
    ax.plot(x_axis, results['validation_0']['error'], label='Train')
    ax.plot(x_axis, results['validation_1']['error'], label='Test')
    ax.legend()
    plt.ylabel('Classification Error')
    plt.title('XGBoost Classification Error')
    plt.show()

    # implement early stopping to find optimal number of boosting rounds
    # if more than one evaluation metric are given the last one is used for
    # early stopping
    m1.xgb_model.fit(m1.X_train, m1.y_train,
                     early_stopping_rounds=10,
                     eval_set=[(m1.X_test, m1.y_test)],
                     eval_metric="logloss",
                     verbose=True)

    print(f"best score: {m1.xgb_model.best_score},"
          f" best iteration: {m1.xgb_model.best_iteration},"
          f" best ntree limit {m1.xgb_model.best_ntree_limit}")

    m1.predict_train_test(m1.xgb_model)
    m1.classification_report()
    m1.evaluate_binary_model()

    def plot_learning_curve(estimator,
                            title,
                            X,
                            y,
                            axes=None,
                            ylim=None,
                            cv=None,
                            n_jobs=None,
                            train_sizes=np.linspace(.1,
                                                    1.0,
                                                    5)):
        """
        Generate 3 plots: the test and training learning curve, the training
        samples vs fit times curve, the fit times vs score curve.

        Parameters
        ----------
        estimator : object type that implements the "fit" and "predict" methods
            An object of that type which is cloned for each validation.

        title : string
            Title for the chart.

        X : array-like, shape (n_samples, n_features)
            Training vector, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape (n_samples) or (n_samples, n_features), optional
            Target relative to X for classification or regression;
            None for unsupervised learning.

        axes : array of 3 axes, optional (default=None)
            Axes to use for plotting the curves.

        ylim : tuple, shape (ymin, ymax), optional
            Defines minimum and maximum yvalues plotted.

        cv : int, cross-validation generator or an iterable, optional
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are:
              - None, to use the default 5-fold cross-validation,
              - integer, to specify the number of folds.
              - :term:`CV splitter`,
              - An iterable yielding (train, test) splits as arrays of indices.

            For integer/None inputs, if ``y`` is binary or multiclass,
            :class:`StratifiedKFold` used. If the estimator is not a classifier
            or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

            Refer :ref:`User Guide <cross_validation>` for the various
            cross-validators that can be used here.

        n_jobs : int or None, optional (default=None)
            Number of jobs to run in parallel.
            ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
            ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
            for more details.

        train_sizes : array-like, shape (n_ticks,), dtype float or int
            Relative or absolute numbers of training examples that will be used to
            generate the learning curve. If the dtype is float, it is regarded as a
            fraction of the maximum size of the training set (that is determined
            by the selected validation method), i.e. it has to be within (0, 1].
            Otherwise it is interpreted as absolute sizes of the training sets.
            Note that for classification the number of samples usually have to
            be big enough to contain at least one sample from each class.
            (default: np.linspace(0.1, 1.0, 5))
        """
        if axes is None:
            _, axes = plt.subplots(1, 3, figsize=(20, 5))

        axes[0].set_title(title)
        if ylim is not None:
            axes[0].set_ylim(*ylim)
        axes[0].set_xlabel("Training examples")
        axes[0].set_ylabel("Score")

        train_sizes, train_scores, test_scores, fit_times, _ = \
            learning_curve(estimator, X, y, cv=cv, n_jobs=n_jobs,
                           train_sizes=train_sizes,
                           return_times=True)
        train_scores_mean = np.mean(train_scores, axis=1)
        train_scores_std = np.std(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        test_scores_std = np.std(test_scores, axis=1)
        fit_times_mean = np.mean(fit_times, axis=1)
        fit_times_std = np.std(fit_times, axis=1)

        # Plot learning curve
        axes[0].grid()
        axes[0].fill_between(train_sizes, train_scores_mean - train_scores_std,
                             train_scores_mean + train_scores_std, alpha=0.1,
                             color="r")
        axes[0].fill_between(train_sizes, test_scores_mean - test_scores_std,
                             test_scores_mean + test_scores_std, alpha=0.1,
                             color="g")
        axes[0].plot(train_sizes, train_scores_mean, 'o-', color="r",
                     label="Training score")
        axes[0].plot(train_sizes, test_scores_mean, 'o-', color="g",
                     label="Cross-validation score")
        axes[0].legend(loc="best")

        # Plot n_samples vs fit_times
        axes[1].grid()
        axes[1].plot(train_sizes, fit_times_mean, 'o-')
        axes[1].fill_between(train_sizes, fit_times_mean - fit_times_std,
                             fit_times_mean + fit_times_std, alpha=0.1)
        axes[1].set_xlabel("Training examples")
        axes[1].set_ylabel("fit_times")
        axes[1].set_title("Scalability of the model")

        # Plot fit_time vs score
        axes[2].grid()
        axes[2].plot(fit_times_mean, test_scores_mean, 'o-')
        axes[2].fill_between(
            fit_times_mean,
            test_scores_mean -
            test_scores_std,
            test_scores_mean +
            test_scores_std,
            alpha=0.1)
        axes[2].set_xlabel("fit_times")
        axes[2].set_ylabel("Score")
        axes[2].set_title("Performance of the model")

        return plt

    title = "Learning Curves (XGBoost)"
    # Cross validation with 100 iterations to get smoother mean test and train
    # score curves, each time with 20% data randomly selected as a validation
    # set.
    cv = ShuffleSplit(n_splits=20, test_size=0.2, random_state=0)

    estimator = m1.xgb_model
    plot_learning_curve(
        estimator, title, m1.X, m1.labels, ylim=(
            0.7, 1.01), cv=cv, n_jobs=4, train_sizes=np.linspace(
            0.001, 1., 100))

    title = r"Learning Curves"
    plt.show()

    # xgb_model feature importance
    plot_importance(m1.xgb_model)

    # plot distribution of a feature based on user group

    # plot the output tree via matplotlib, specifying the ordinal number of
    # the target tree
    plot_tree(m1.xgb_model, num_trees=m1.xgb_model.best_iteration)

    ############################# SAVE MODEL #############################
    m1.save_model(m1.rf_model)

    print('\n _______________ Testing on another dataset ________________')
    df = pd.read_csv('human_org_features_labels_noNan.csv', index_col=0)
    labels = np.array(df.pop('labels'))
    pred = m1.xgb_model.predict(df)
    cm = confusion_matrix(labels, pred)
    print(cm)
    print(classification_report(labels, pred))

    # In[]:

    # multiclass (multilabel) classifier

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

    m1.train_predict_evaluate_OneVsRestClassifier(m1.xgb_model, True)
    m1.train_predict_evaluate_OneVsRestClassifier(m1.rf_model)
    m1.train_predict_evaluate_OneVsRestClassifier(m1.rf_model, True)
    m1.train_predict_evaluate_OneVsRestClassifier(m1.adab_model, True)

    # change threshold (multilabel) based on required_threshold
    required_precision = 0.95

    pall = m1.OVRClassifier.predict(m1.X_test)  # the "global" prediction
    p0 = m1.OVRClassifier.estimators_[0].predict(
        m1.X_test)  # the first-class prediction
    p1 = m1.OVRClassifier.estimators_[1].predict(
        m1.X_test)  # the second-class prediction
    p2 = m1.OVRClassifier.estimators_[2].predict(
        m1.X_test)  # the third-class prediction
    prob0 = m1.OVRClassifier.estimators_[0].predict_proba(m1.X_test)[:, 1]
    prob1 = m1.OVRClassifier.estimators_[1].predict_proba(m1.X_test)[:, 1]
    prob2 = m1.OVRClassifier.estimators_[2].predict_proba(m1.X_test)[:, 1]

    precisions0, recalls0, thresholds0 = precision_recall_curve(
        m1.y_test.T[0], prob0)
    precisions1, recalls1, thresholds1 = precision_recall_curve(
        m1.y_test.T[1], prob1)
    precisions2, recalls2, thresholds2 = precision_recall_curve(
        m1.y_test.T[2], prob2)

    threshold_required0 = thresholds0[precisions0[:-1] >= required_precision]
    threshold_required1 = thresholds1[precisions1[:-1] >= required_precision]
    threshold_required2 = thresholds2[precisions2[:-1] >= required_precision]

    p0_new = (prob0 > threshold_required0[0]).astype(int)
    p1_new = (prob1 > threshold_required1[0]).astype(int)
    p2_new = (prob2 > threshold_required2[0]).astype(int)

    print(classification_report(m1.y_test.T[0], p0_new))
    print(classification_report(m1.y_test.T[1], p1_new))
    print(classification_report(m1.y_test.T[2], p2_new))

    pall_new = np.array([p0_new, p1_new, p2_new]).T
    print(classification_report(m1.y_test, pall_new))

    ########## multiclass classification confusion matrix ####################
    print(pd.crosstab(m1.y_test, m1.pred_test, rownames=['True'],
                      colnames=['Predicted']))

    # fine-tunning rf- method 1: grid search for maximising a score
    param_grid_rf = {
        'min_samples_split': [3, 5, 10],
        'n_estimators': [100, 300],
        'max_depth': [3, 5, 15, 25],
        'max_features': [3, 5, 10, 20]
    }

    param_grid_gb = {
        "loss": ["deviance"],
        "learning_rate": [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2],
        "min_samples_split": np.linspace(0.1, 0.5, 12),
        "min_samples_leaf": np.linspace(0.1, 0.5, 12),
        "max_depth": [15, 20, 25, 30],
        "max_features": ["log2", "sqrt"],
        "criterion": ["friedman_mse", "mae"],
        "subsample": [0.5, 0.618, 0.8, 0.85, 0.9, 0.95, 1.0],
        "n_estimators": [100, 200]
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
