#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:45:36 2020

@author: johannesheyl
"""

import spacy
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nlp = spacy.load('en', disable=['parser', 'ner'])
# this function receives comments and returns clean word-list
def clean_doc(text_record):
    # split tokens by white space
    tokens = text_record.split()
    # remove punctuation from each string
    table = str.maketrans({key: None for key in string.punctuation})
    tokens = [token.translate(table) for token in tokens]
    # remove tokens that are not alphabetic
    tokens = [token for token in tokens if token.isalpha()]
    # convert letters to lower case
    tokens = [token.lower() for token in tokens]
    # remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    # remove short words (one letter)
    tokens = [token for token in tokens if len(token) > 1]
    # lemmatization
    lem = WordNetLemmatizer()
    tokens = [lem.lemmatize(token) for token in tokens]
    sentence = ' '.join(tokens)
    tokens = sentence.split()
    doc = nlp(" ".join(tokens))
    tokens=[token.lemma_ for token in doc if token.pos_ in ['NOUN', 'ADJ', 'VERB', 'ADV']]
    sentence = ' '.join(tokens)
    return sentence