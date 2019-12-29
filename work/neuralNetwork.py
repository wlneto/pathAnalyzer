################################################################################
# Libraries
################################################################################
import pickle
import numpy as np
# from tabulate import tabulate
import os
import tensorflow as tf
import plotly.graph_objects as go
# import pprint
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
################################################################################
# Config
################################################################################
epochs = 100
dataTypeTrainLabel = "Train"
dataTypeValidationLabel = "Validation"
dataTypeTestLabel = "Test"
dataTypeKey = "dataType"
featureTensorKey = "featureTensor"
labelKey = "label"
datasetFileName = "dataset.pkl"
################################################################################
# Load Dataset
################################################################################
if os.path.exists(datasetFileName):
	with open(datasetFileName, 'rb') as f:
		dataset = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (datasetFileName))
# print(tabulate(dataset, headers='keys', tablefmt='psql'))
################################################################################
# Prepare data
################################################################################
print("Splitting training, validation and test data")
trainFeatureList = []
trainLabelList = []
for datasetIdx, datasetRow in dataset[dataset[dataTypeKey] == dataTypeTrainLabel].iterrows():
	trainFeatureList.append(datasetRow[featureTensorKey])
	trainLabelList.append(datasetRow[labelKey])
trainSetSize = len(trainLabelList)
print("  Training set size = %d" % trainSetSize)
validationFeatureList = []
validationLabelList = []
for datasetIdx, datasetRow in dataset[dataset[dataTypeKey] == dataTypeValidationLabel].iterrows():
	validationFeatureList.append(datasetRow[featureTensorKey])
	validationLabelList.append(datasetRow[labelKey])
validationSetSize = len(validationLabelList)
print("  Validation set size = %d" % validationSetSize)
testFeatureList = []
testLabelList = []
for datasetIdx, datasetRow in dataset[dataset[dataTypeKey] == dataTypeTestLabel].iterrows():
	testFeatureList.append(datasetRow[featureTensorKey])
	testLabelList.append(datasetRow[labelKey])
testSetSize = len(testLabelList)
print("  Test set size = %d" % testSetSize)
print("Preparing Numpy Arrays")
maxPathSize = len(trainFeatureList[0])
cellFeatureSize = len(trainFeatureList[0][0])
featureTensorShape = (maxPathSize, cellFeatureSize, 1)
print("  Feature tensor shape = %s" % str(featureTensorShape))
trainFeatureList = np.array(trainFeatureList)
trainFeatureList = trainFeatureList.reshape(trainSetSize, maxPathSize, cellFeatureSize, 1)
trainLabelList = np.array(trainLabelList)
trainLabelList = trainLabelList.reshape(trainSetSize, 1)
validationFeatureList = np.array(validationFeatureList)
validationFeatureList = validationFeatureList.reshape(validationSetSize, maxPathSize, cellFeatureSize, 1)
validationLabelList = np.array(validationLabelList)
validationLabelList = validationLabelList.reshape(validationSetSize, 1)
testFeatureList = np.array(testFeatureList)
testFeatureList = testFeatureList.reshape(testSetSize, maxPathSize, cellFeatureSize, 1)
testLabelList = np.array(testLabelList)
testLabelList = testLabelList.reshape(testSetSize, 1)
################################################################################
# Create neural network
################################################################################
print("Creating Neural Network")
# Clearup everything before running
tf.keras.backend.clear_session()
# Create model
model = tf.keras.models.Sequential()
# Add layers
model.add(tf.keras.layers.Conv2D(32, (2,2), activation='relu', input_shape=featureTensorShape))
# tf.keras.layers.AveragePooling2D(2, 2),
# model.add(tf.keras.layers.Conv2D(64, (2,2), activation='relu'))
# model.add(tf.keras.layers.Conv2D(32, (2,2), activation='relu'))
# model.add(tf.keras.layers.Conv2D(32, (2,2), activation='relu'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(64, activation='relu'))
# model.add(tf.keras.layers.Dense(1024, activation='relu'))
# model.add(tf.keras.layers.Dense(1024, activation='relu'))
# model.add(tf.keras.layers.Dense(1024, activation='relu'))
model.add(tf.keras.layers.Dense(1))
################################################################################
# Train neural network
################################################################################
print("Training Neural Network")
# Print summary
model.summary()
lossFunction = 'mean_absolute_error'
# lossFunction = 'mean_squared_error'
# lossFunction = 'mean_squared_logarithmic_error'
history = model.compile(optimizer='adam', loss=lossFunction, metrics=[lossFunction])
# # history.history.keys()
# # history.history
history = model.fit(trainFeatureList,trainLabelList,
                    epochs=epochs, verbose=2,
                    validation_data=(validationFeatureList,validationLabelList))
# Plot training info
lossListY = history.history["loss"]
lossListX = list(range(len(lossListY)))
valLossListY = history.history["val_loss"]
valLossListX = list(range(len(valLossListY)))
fig0 = go.Figure(data=[go.Scatter(x=lossListX,y=lossListY,name="Training Loss"),
                       go.Scatter(x=valLossListX,y=valLossListY,name="Validation Loss")])
fig0.show()
################################################################################
# Check validation data
################################################################################
print("Checking validation data")
print("  Found %d labels" % len(testLabelList))
testPredictList = model.predict(testFeatureList)
print("  Collected %d predictions" % len(testPredictList))
testPredictList = testPredictList.reshape(len(testPredictList))
testLabelList = testLabelList.reshape(len(testLabelList))
testErrorList = []
testErrorLargerList = []
testErrorSmallerList = []
for label, predict in zip(testLabelList, testPredictList):
	error = label/predict
	if error < 1.0:
		error = 1.0 - error
		testErrorSmallerList.append(error)
	else:
		error = error - 1.0
		testErrorLargerList.append(error)
	testErrorList.append(error)
fig1 = go.Figure(data=[go.Scatter(x=testLabelList,y=testPredictList,text=testErrorList,mode="markers",name="Prediction"),go.Scatter(x=testLabelList,y=testLabelList,name="Ideal"),go.Scatter(x=testLabelList,y=1.1*testLabelList),go.Scatter(x=testLabelList,y=0.9*testLabelList)])
fig1.update_layout(title="Max Error = %f" % max(testErrorList))
fig1.show()
