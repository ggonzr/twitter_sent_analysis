"""
Modelo de aprendizaje automatico
"""
# Tensorflow
from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow as tf

# Keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import (
    Activation,
    Dense,
    Dropout,
    Embedding,
    Flatten,
    Conv1D,
    MaxPooling1D,
    LSTM,
)
from keras import utils
from keras.callbacks import ReduceLROnPlateau, EarlyStopping

# nltk
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

# Word2vec
import gensim

# Utility
import re
import numpy as np
import os
from collections import Counter
import logging
import time
import pickle
import itertools

# Variables globales
# ----------------------------------------------------

model = None
tokenizer = None
encoder = None
w2v_model = None

# Constantes
# -------------------------------------------------------------

DATASET_COLUMNS = ["target", "ids", "date", "flag", "user", "text"]
DATASET_ENCODING = "ISO-8859-1"
TRAIN_SIZE = 0.8

# TEXT CLENAING
TEXT_CLEANING_RE = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"

# WORD2VEC
W2V_SIZE = 300
W2V_WINDOW = 7
W2V_EPOCH = 32
W2V_MIN_COUNT = 10

# KERAS
SEQUENCE_LENGTH = 300
EPOCHS = 8
BATCH_SIZE = 1024

# SENTIMENT
POSITIVE = "POSITIVE"
NEGATIVE = "NEGATIVE"
NEUTRAL = "NEUTRAL"
SENTIMENT_THRESHOLDS = (0.4, 0.7)

# EXPORT
KERAS_MODEL = "../model/model.h5"
WORD2VEC_MODEL = "../model/model.w2v"
TOKENIZER_MODEL = "../model/tokenizer.pkl"
ENCODER_MODEL = "../model/encoder.pkl"
# -------------------------------------------------------------

# Funciones
# -------------------------------------------------------------
def init():
    """
    Permite cargar el modelo a memoria y dejarlo disponible para su uso
    """
    global model, tokenizer, encoder, w2v_model

    # Set log
    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
    )
    tf.keras.backend.clear_session()  # Para restablecer fácilmente el estado del portátil.

    # Objetos a cargar desde binario
    with open(TOKENIZER_MODEL, "rb") as tk:
        tokenizer = pickle.load(file=tk)
    with open(ENCODER_MODEL, "rb") as ec:
        encoder = pickle.load(file=ec)

    # Word2Vec
    w2v_model = gensim.models.word2vec.Word2Vec.load(WORD2VEC_MODEL)
    model = tf.keras.models.load_model(KERAS_MODEL)
    message = (
        f"Verificacion rapida con tipo - model = {type(model)}",
        f"w2v_model = {w2v_model}",
        f"tokenizer = {tokenizer}",
        f"encoder = {encoder}",
    )
    print(message)


def decode_sentiment(score, include_neutral=True) -> str:
    if include_neutral:
        label = NEUTRAL
        if score <= SENTIMENT_THRESHOLDS[0]:
            label = NEGATIVE
        elif score >= SENTIMENT_THRESHOLDS[1]:
            label = POSITIVE

        return label
    else:
        return NEGATIVE if score < 0.5 else POSITIVE


def predict(text, include_neutral=True) -> dict:
    start_at = time.time()
    # Tokenize text
    x_test = pad_sequences(tokenizer.texts_to_sequences([text]), maxlen=SEQUENCE_LENGTH)
    # Predict
    score = model.predict([x_test])[0]
    # Decode sentiment
    label = decode_sentiment(score, include_neutral=include_neutral)

    return {
        "label": label,
        "score": float(score),
        "elapsed_time": time.time() - start_at,
    }
