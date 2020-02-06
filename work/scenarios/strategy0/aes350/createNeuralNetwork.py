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
from plotly.subplots import make_subplots
sys.path.append(os.path.realpath("../../../../src"))
from PathDataset import PathDataset
# import pprint
# from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
################################################################################
# Config
################################################################################
datasetsFolder = "../../../datasets"
strategy = 0
testCircuitName = "aes"
testCircuitDelay = 350
trainCircuit = "pico-rv"
epochs = 100
dataTypeKey = "dataType"
featureTensorKey = "featureTensor"
labelKey = "label"
trainDatasetFileName = datasetsFolder+"/"+trainCircuit+"TrainDatasetFullStrategy"+str(strategy)+".pkl"
testDatasetFileName = datasetsFolder+"/"+testCircuitName+"TestDataset"+str(testCircuitDelay)+"Strategy"+str(strategy)+".pkl"
outlierErrorThreshold = 0.1
outlierList = []
checkpointPath = "neuralNetworkTraining/nn~{epoch:04d}.ckpt"
checkpointFreq = 10
################################################################################
# Load Dataset
################################################################################
print("Collecting trainDataset")
if os.path.exists(trainDatasetFileName):
	with open(trainDatasetFileName, 'rb') as f:
		trainDataset = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (trainDatasetFileName))
# print(tabulate(trainDataset, headers='keys', tablefmt='psql'))
print("Collecting testDataset")
if os.path.exists(testDatasetFileName):
	with open(testDatasetFileName, 'rb') as f:
		testDataset = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (testDatasetFileName))
# print(tabulate(testDataset, headers='keys', tablefmt='psql'))
################################################################################
# Collect data
################################################################################
# print("Moving outliars to training set")
# for outlier in outlierList:
# 	trainDataset.loc[outlier, dataTypeKey] = dataTypeTrainLabel
print("Collecting training, validation and test data")
trainDatasetDF=trainDataset.dataset
trainFeatureList = []
trainLabelList = []
for trainDatasetIdx, trainDatasetRow in trainDatasetDF[trainDatasetDF[PathDataset.dataTypeKey] == PathDataset.trainDataLabel].iterrows():
	trainFeatureList.append(trainDatasetRow[PathDataset.featureTensorKey])
	trainLabelList.append(trainDatasetRow[PathDataset.labelKey])
trainSetSize = len(trainLabelList)
print("  Training set size = %d" % trainSetSize)
validationFeatureList = []
validationLabelList = []
for trainDatasetIdx, trainDatasetRow in trainDatasetDF[trainDatasetDF[PathDataset.dataTypeKey] == PathDataset.validationDataLabel].iterrows():
	validationFeatureList.append(trainDatasetRow[PathDataset.featureTensorKey])
	validationLabelList.append(trainDatasetRow[PathDataset.labelKey])
validationSetSize = len(validationLabelList)
print("  Validation set size = %d" % validationSetSize)
# Variable to collect maxPathSize size and add padding when needed
maxPathSize = len(trainFeatureList[0])
padding = [0.0] * len(trainFeatureList[0][0])
testDatasetDF=testDataset.dataset
testFeatureList = []
testLabelList = []
startpointList = []
endpointList = []
for testDatasetIdx, testDatasetRow in testDatasetDF[testDatasetDF[PathDataset.dataTypeKey] == PathDataset.testDataLabel].iterrows():
	feature = testDatasetRow[PathDataset.featureTensorKey]
	while len(feature) < maxPathSize:
		feature.append(padding)
	testFeatureList.append(feature)
	# testFeatureList.append(testDatasetRow[PathDataset.featureTensorKey])
	testLabelList.append(testDatasetRow[PathDataset.labelKey])
	startpointList.append(testDatasetRow["startpoint"])
	endpointList.append(testDatasetRow["endpoint"])
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
convFilterDim = len(testFeatureList[0][0])
# Clearup everything before running
tf.keras.backend.clear_session()
# Create model
model = tf.keras.models.Sequential()
# Add layers
# model.add(tf.keras.layers.Dense(8, activation='relu', input_shape=featureTensorShape))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Conv2D(32, (convFilterDim,convFilterDim), activation='sigmoid', input_shape=featureTensorShape))
model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Conv2D(32, (3,3), activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Conv2D(32, (2,1), activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Flatten())
# model.add(tf.keras.layers.Dense(16, activation='sigmoid'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(16, activation='sigmoid'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(32, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(32, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(32, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
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
# lossFunction = 'mean_squared_error'
# lossFunction = 'mean_absolute_error'
history = model.compile(optimizer='adam', loss=lossFunction, metrics=["accuracy"])
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
testPredictList = testPredictList.reshape(len(testPredictList))
testLabelList = testLabelList.reshape(len(testLabelList))
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
# Bin classifier error analysis
fig = make_subplots(rows=2, cols=1, subplot_titles=("Label 0", "Label 1"))
label0List = []
label1List = []
for label, predict in zip(testLabelList, testPredictList):
	if label == 0:
		label0List.append(predict)
	elif label == 1:
		label1List.append(predict)
	else:
		raise RuntimeError("Unexpected error! Read label %s" % str(label))

fig.add_trace(go.Histogram(x=label0List), row=1, col=1)
fig.add_trace(go.Histogram(x=label1List), row=2, col=1)
fig.update_layout(title="Binary classifier prediction error", height=900, width=1800, showlegend=False)
fig.show()
truePositive = 0
trueNegative = 0
falsePositive = 0
falseNegative = 0
for label, predict in zip(testLabelList, testPredictList):
	if predict >= 0.5:
		if label == 1:
			truePositive += 1
		else:
			falsePositive += 1
	else:
		if label == 0:
			trueNegative += 1
		else:
			falseNegative += 1
precision = truePositive / (truePositive+falsePositive)
recall = truePositive / (truePositive+falseNegative)
f1Score = 2*(precision*recall)/(precision+recall)
print("\tPred. Neg\tPred. Pos")
print("Act. Neg\t%d\t%d" % (trueNegative, falsePositive))
print("Act. Pos\t%d\t%d" % (falseNegative, truePositive))
print("Precision = %f" % precision)
print("Recall = %f" % recall)
print("F1 = %f" % f1Score)
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
################################################################################
# Generate SDC
################################################################################
f = open("nn_optimize.sdc", "w")
f2 = open("nn_revert.sdc", "w")
for testPredict, startpoint, endpoint in zip(testPredictList, startpointList, endpointList):
	if testPredict > 0.5:
		f.write("set_max_delay 0 -from %s -to %s\n" % (startpoint, endpoint))
		f2.write("set_max_delay %s -from %s -to %s\n" % (testCircuitDelay, startpoint, endpoint))
f.close()
f2.close()
