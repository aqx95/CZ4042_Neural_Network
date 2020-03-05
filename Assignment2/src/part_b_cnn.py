# -*- coding: utf-8 -*-
"""Part_B_CNN

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GP7v2CfMpx1p_XUoGrNn0TnlLqqFCK0o
"""

from google.colab import drive
drive.mount('/content/drive')

# Dependencies and constants
import numpy as np
import pandas
import tensorflow as tf
import csv
import matplotlib.pyplot as plt
import time

MAX_DOCUMENT_LENGTH = 100
N_FILTERS = 10
FILTER_SHAPE1 = [20, 256]
FILTER_SHAPE2 = [20, 1]

POOLING_WINDOW = 4
POOLING_STRIDE = 2
MAX_LABEL = 15

no_epochs = 500
lr = 0.01
batch_size = 128

# Good value for dropout in hidden layer is btw 0.5-0.8. Input layer uses a larger
# dropout rate such as 0.8
dropout = 0.5

tf.logging.set_verbosity(tf.logging.ERROR)
seed = 10
tf.set_random_seed(seed)

# Read Character
def read_data_chars():
  
  x_train, y_train, x_test, y_test = [], [], [], []

  with open('drive/My Drive/train_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_train.append(row[1])
      y_train.append(int(row[0]))

  with open('drive/My Drive/test_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_test.append(row[1])
      y_test.append(int(row[0]))
  
  x_train = pandas.Series(x_train)
  y_train = pandas.Series(y_train)
  x_test = pandas.Series(x_test)
  y_test = pandas.Series(y_test)
  
  
  char_processor = tf.contrib.learn.preprocessing.ByteProcessor(MAX_DOCUMENT_LENGTH)
  x_train = np.array(list(char_processor.fit_transform(x_train)))
  x_test = np.array(list(char_processor.transform(x_test)))
  y_train = y_train.values
  y_test = y_test.values
  
  return x_train, y_train, x_test, y_test

# Read Words
def data_read_words():
  
  x_train, y_train, x_test, y_test = [], [], [], []
  
  with open('drive/My Drive/train_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_train.append(row[2])
      y_train.append(int(row[0]))

  with open('drive/My Drive/test_medium.csv', encoding='utf-8') as filex:
    reader = csv.reader(filex)
    for row in reader:
      x_test.append(row[2])
      y_test.append(int(row[0]))
  
  x_train = pandas.Series(x_train)
  y_train = pandas.Series(y_train)
  x_test = pandas.Series(x_test)
  y_test = pandas.Series(y_test)
  y_train = y_train.values
  y_test = y_test.values
  
  vocab_processor = tf.contrib.learn.preprocessing.VocabularyProcessor(
      MAX_DOCUMENT_LENGTH)

  x_transform_train = vocab_processor.fit_transform(x_train)
  x_transform_test = vocab_processor.transform(x_test)

  x_train = np.array(list(x_transform_train))
  x_test = np.array(list(x_transform_test))

  no_words = len(vocab_processor.vocabulary_)
  print('Total words: %d' % no_words)

  return x_train, y_train, x_test, y_test, no_words

# CNN (char level)
def char_cnn_model(x, dropoutBoolean):
  
  input_layer = tf.reshape(
      tf.one_hot(x, 256), [-1, MAX_DOCUMENT_LENGTH, 256, 1])
  
  if dropoutBoolean:
    scopeName = "CNN_Layer1_Dropout"
  else:
    scopeName = "CNN_Layer1"

  with tf.variable_scope(scopeName):
    conv1 = tf.layers.conv2d(
        input_layer,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE1,
        padding='VALID',
        activation=tf.nn.relu)
    
    pool1 = tf.layers.max_pooling2d(
        conv1,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')
    
    if dropoutBoolean:
      pool1 = tf.nn.dropout(pool1, dropout)

 # second convolution and pooling layer   
    conv2 = tf.layers.conv2d(
        pool1,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE2,
        padding='VALID',
        activation=tf.nn.relu)
    
    pool2 = tf.layers.max_pooling2d(
        conv2,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')
    
    if dropoutBoolean:
      pool2 = tf.nn.dropout(pool2, dropout)

    pool2 = tf.squeeze(tf.reduce_max(pool2, 1), squeeze_dims=[1])

  logits = tf.layers.dense(pool2, MAX_LABEL, activation=None)

  return input_layer,logits

# CNN (Word level)
def word_cnn_model(x, dropoutBoolean):
  
  word_vectors = tf.contrib.layers.embed_sequence(x, vocab_size=n_words, embed_dim=EMBEDDING_SIZE)

  input_layer = tf.reshape(
      word_vectors, [-1, MAX_DOCUMENT_LENGTH, EMBEDDING_SIZE, 1])
  
  if dropoutBoolean:
    scopeName = "CNN_Layer2_Dropout"
  else:
    scopeName = "CNN_Layer2"

  with tf.variable_scope(scopeName):
    conv1 = tf.layers.conv2d(
        input_layer,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE1,
        padding='VALID',
        activation=tf.nn.relu)
    
    pool1 = tf.layers.max_pooling2d(
        conv1,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')
    
    if dropoutBoolean:
      pool1 = tf.nn.dropout(pool1, dropout)

 # second convolution and pooling layer   
    conv2 = tf.layers.conv2d(
        pool1,
        filters=N_FILTERS,
        kernel_size=FILTER_SHAPE2,
        padding='VALID',
        activation=tf.nn.relu)
    
    pool2 = tf.layers.max_pooling2d(
        conv2,
        pool_size=POOLING_WINDOW,
        strides=POOLING_STRIDE,
        padding='SAME')
    
    if dropoutBoolean:
      pool2 = tf.nn.dropout(pool2, dropout)

    pool2 = tf.squeeze(tf.reduce_max(pool2, 1), squeeze_dims=[1])

  logits = tf.layers.dense(pool2, MAX_LABEL, activation=None)

  return input_layer, logits

# Main training loop for character CNN
def main(dropoutBoolean):
  
  x_train, y_train, x_test, y_test = read_data_chars()

  print(len(x_train))
  print(len(x_test))

  # Create the model
  x = tf.placeholder(tf.int64, [None, MAX_DOCUMENT_LENGTH])
  y_ = tf.placeholder(tf.int64)

  if dropoutBoolean:
    inputs, logits = char_cnn_model(x, True)
  else:
    inputs, logits = char_cnn_model(x, False)

  # Optimizer
  entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=tf.one_hot(y_, MAX_LABEL), logits=logits))
  train_op = tf.train.AdamOptimizer(lr).minimize(entropy)

  # Accuracy
  prediction = tf.argmax(logits, 1)
  equality = tf.equal(prediction, y_)
  accuracy = tf.reduce_mean(tf.cast(equality, tf.float32))



  # training
  loss = []
  accuracyList = []
  
  # Shuffle data
  N = len(x_train)
  index = np.arange(N)

  # Start timer right before running model
  timer = time.time()

  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    for e in range(no_epochs):
      np.random.shuffle(index)
      x_train, y_train = x_train[index], y_train[index]

      for start, end in zip(range(0,N, batch_size), range(batch_size, N, batch_size)):
        train_op.run(feed_dict={x:x_train[start:end], y_:y_train[start:end]})
      
      _, loss_  = sess.run([train_op, entropy], {x: x_train, y_: y_train})
      loss.append(loss_)

      acc_temp = accuracy.eval(feed_dict={x:x_test, y_:y_test})
      accuracyList.append(acc_temp)

      if e%1 == 0:
        print('iter: %d, entropy: %g, accuracy: %g'%(e, loss[e], accuracyList[e]))
  
  sess.close()

  totalTime = time.time() - timer
  print("Total Time taken: ", totalTime)

  # plt.plot(range(len(loss)), loss, label="loss")
  # plt.plot(range(len(accuracyList)), accuracyList, label="accuracy")
  # plt.legend()
  # plt.xlabel("epochs")
  # plt.ylabel("Accuracy/Loss")
  # plt.show()


  plt.figure(1)

  plt.plot(range(no_epochs), loss, "b", label="train loss")
  plt.plot(range(no_epochs), accuracyList,"m", label="test accuracy ")

  plt.ylabel("Test Accuracy | Loss")
  plt.xlabel("epochs")

  plt.legend()
  plt.show()


if __name__ == '__main__':
  main(True)

  main(False)

# Main training loop for CNN (word)
def main(dropoutBoolean):
  global n_words

  x_train, y_train, x_test, y_test, n_words = data_read_words()


  print(len(x_train))
  print(len(x_test))

  # Create the model
  x = tf.placeholder(tf.int64, [None, MAX_DOCUMENT_LENGTH])
  y_ = tf.placeholder(tf.int64)

  if dropoutBoolean:
    inputs, logits = word_cnn_model(x, True)
  else:
    inputs, logits = word_cnn_model(x, False)

  # Optimizer
  entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(labels=tf.one_hot(y_, MAX_LABEL), logits=logits))
  train_op = tf.train.AdamOptimizer(lr).minimize(entropy)

  # Accuracy
  prediction = tf.argmax(logits, 1)
  equality = tf.equal(prediction, y_)
  accuracy = tf.reduce_mean(tf.cast(equality, tf.float32))


  # training
  loss = []
  accuracyList = []
  
  # Shuffle data
  N = len(x_train)
  index = np.arange(N)

  # Start timer right before running model
  timer = time.time()

  with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())

    for e in range(no_epochs):
      np.random.shuffle(index)
      x_train, y_train = x_train[index], y_train[index]

      for start, end in zip(range(0,N, batch_size), range(batch_size, N, batch_size)):
        train_op.run(feed_dict={x:x_train[start:end], y_:y_train[start:end]})
      
      _, loss_  = sess.run([train_op, entropy], {x: x_train, y_: y_train})
      loss.append(loss_)

      acc_temp = accuracy.eval(feed_dict={x:x_test, y_:y_test})
      accuracyList.append(acc_temp)

      if e%1 == 0:
        print('iter: %d, entropy: %g, accuracy: %g'%(e, loss[e], accuracyList[e]))
  
  sess.close()

  totalTime = time.time() - timer
  print("Total Time taken: ", totalTime)

  # plt.plot(range(len(loss)), loss, label="loss")
  # plt.plot(range(len(accuracyList)), accuracyList, label="accuracy")
  # plt.legend()
  # plt.xlabel("epochs")
  # plt.ylabel("Accuracy/Loss")
  # plt.show()


  plt.figure(1)

  plt.plot(range(no_epochs), loss, "b", label = "train loss")
  plt.plot(range(no_epochs), accuracyList,"m", label = "test accuracy")

  plt.ylabel("Accuracy | Loss")
  plt.xlabel("Epochs")

  plt.legend()
  plt.show()


if __name__ == '__main__':
  main(True)
  main(False)