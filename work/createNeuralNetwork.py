################################################################################
# Libraries
################################################################################
import pickle
import numpy as np
# from tabulate import tabulate
import os
import sys
import tensorflow as tf
import plotly.graph_objects as go
sys.path.append(os.path.realpath("../src"))
from PathDataset import PathDataset
# import pprint
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
################################################################################
# Config
################################################################################
epochs = 500
dataTypeKey = "dataType"
featureTensorKey = "featureTensor"
labelKey = "label"
datasetFileName = "synGenDataset.pkl"
outlierErrorThreshold = 0.1
outlierList = []
checkpointPath = "neuralNetworkTraining/nn~{epoch:04d}.ckpt"
checkpointFreq = 20
################################################################################
# Load Dataset
################################################################################
print("Collecting dataset")
if os.path.exists(datasetFileName):
	with open(datasetFileName, 'rb') as f:
		dataset = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (datasetFileName))
# print(tabulate(dataset, headers='keys', tablefmt='psql'))
################################################################################
# Collect data
################################################################################
# print("Moving outliars to training set")
# for outlier in outlierList:
# 	dataset.loc[outlier, dataTypeKey] = dataTypeTrainLabel
print("Collecting training, validation and test data")
datasetDF=dataset.dataset
trainFeatureList = []
trainLabelList = []
for datasetIdx, datasetRow in datasetDF[datasetDF[PathDataset.dataTypeKey] == PathDataset.trainDataLabel].iterrows():
	trainFeatureList.append(datasetRow[PathDataset.featureTensorKey])
	trainLabelList.append(datasetRow[PathDataset.labelKey])
trainSetSize = len(trainLabelList)
print("  Training set size = %d" % trainSetSize)
validationFeatureList = []
validationLabelList = []
for datasetIdx, datasetRow in datasetDF[datasetDF[PathDataset.dataTypeKey] == PathDataset.validationDataLabel].iterrows():
	validationFeatureList.append(datasetRow[PathDataset.featureTensorKey])
	validationLabelList.append(datasetRow[PathDataset.labelKey])
validationSetSize = len(validationLabelList)
print("  Validation set size = %d" % validationSetSize)
testFeatureList = []
testLabelList = []
for datasetIdx, datasetRow in datasetDF[datasetDF[PathDataset.dataTypeKey] == PathDataset.testDataLabel].iterrows():
	testFeatureList.append(datasetRow[PathDataset.featureTensorKey])
	testLabelList.append(datasetRow[PathDataset.labelKey])
testSetSize = len(testLabelList)
print("  Test set size = %d" % testSetSize)
################################################################################
# Prepare data
################################################################################
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
# model.add(tf.keras.layers.Dense(8, activation='relu', input_shape=featureTensorShape))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Conv2D(16, (3,3), activation='relu', input_shape=featureTensorShape))
model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Conv2D(16, (2,2), activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Conv2D(16, (1,2), activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(32, activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Dense(32, activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(512, activation='relu'))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dense(1024, activation='relu'))
# model.add(tf.keras.layers.Dense(1))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
################################################################################
# Train neural network
################################################################################
print("Training Neural Network")
# Print summary
model.summary()
# Checkpoint callback
checkpointDir = os.path.dirname(checkpointPath)
cpCallback = tf.keras.callbacks.ModelCheckpoint(checkpointPath, save_weights_only=True, verbose=1, period=checkpointFreq)
lossFunction = 'binary_crossentropy'
# lossFunction = 'mean_squared_logarithmic_error'
history = model.compile(optimizer='adam', loss=lossFunction, metrics=['accuracy'])
# # history.history.keys()
# # history.history
history = model.fit(trainFeatureList,trainLabelList,
                    epochs=epochs, verbose=2,
                    validation_data=(validationFeatureList,validationLabelList),
                    callbacks = [cpCallback])
# Plot training info
lossListY = history.history["loss"]
lossListX = list(range(len(lossListY)))
valLossListY = history.history["val_loss"]
valLossListX = list(range(len(valLossListY)))
fig0 = go.Figure(data=[go.Scatter(x=lossListX,y=lossListY,name="Training Loss"),
                       go.Scatter(x=valLossListX,y=valLossListY,name="Validation Loss")])
fig0.show()
################################################################################
# Check test data
################################################################################
print("Checking test data")
print("  Found %d labels" % len(testLabelList))
testPredictList = model.predict(testFeatureList)
print("  Collected %d predictions" % len(testPredictList))
# print(testPredictList)
truePositive = 0
trueNegative = 0
falsePositive = 0
falseNegative = 0
for predict, label in zip(testPredictList, testLabelList):
	if predict > 0.5:
		if label == 1:
			truePositive += 1
		else:
			falsePositive += 1
	else:
		if label == 0:
			trueNegative += 1
		else:
			falseNegative += 1
print("\tPos\tNeg")
print("True\t%d\t%d" % (truePositive, trueNegative))
print("False\t%d\t%d" % (falsePositive, falseNegative))
total = truePositive + falsePositive + trueNegative + falseNegative
accuracy = (truePositive + trueNegative) / total
print("Test accuracy = %f" % accuracy)
# testPredictList = testPredictList.reshape(len(testPredictList))
# testLabelList = testLabelList.reshape(len(testLabelList))
# testErrorList = []
# testErrorLargerList = []
# testErrorSmallerList = []
# for label, predict in zip(testLabelList, testPredictList):
# 	error = label/predict
# 	if error < 1.0:
# 		error = 1.0 - error
# 		testErrorSmallerList.append(error)
# 	else:
# 		error = error - 1.0
# 		testErrorLargerList.append(error)
# 	testErrorList.append(error)
# testErrorMean = sum(testErrorList)/len(testErrorList)
# fig1 = go.Figure(data=[go.Scatter(x=testLabelList,y=testPredictList,text=testErrorList,mode="markers",name="Prediction"),go.Scatter(x=testLabelList,y=testLabelList,name="Ideal"),go.Scatter(x=testLabelList,y=1.1*testLabelList),go.Scatter(x=testLabelList,y=0.9*testLabelList)])
# fig1.update_layout(title="Max Error = %f" % max(testErrorList))
# fig1.show()
# fig2 = go.Figure(data=[go.Histogram(x=testErrorList)])
# fig2.update_layout(title="Error Distribution (Mean Error = %f)" % testErrorMean)
# fig2.show()
# ################################################################################
# # Get outliers
# ################################################################################
# outlierList = []
# testIdx=0
# for error in testErrorList:
# 	if error > outlierErrorThreshold:
# 		outlierList.append(testIdxList[testIdx])
# 	testIdx = testIdx + 1
# print("Outliers are:")
# print(outlierList)
