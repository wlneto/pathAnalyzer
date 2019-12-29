################################################################################
# Libraries
################################################################################
import pickle
import numpy as np
import os
import tensorflow as tf
################################################################################
# Config
################################################################################
epochs = 2000
dataTypeTrainLabel = "Train"
dataTypeValidationLabel = "Validation"
dataTypeTestLabel = "Test"
dataTypeKey = "dataType"
featureTensorKey = "featureTensor"
labelKey = "label"
datasetFileName = "../dataset.pkl"
outputFileName = "neuralNetwork13.pkl"
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
model.add(tf.keras.layers.Conv2D(64, (2,2), activation='relu', input_shape=featureTensorShape))
model.add(tf.keras.layers.Conv2D(64, (2,2), activation='relu'))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dense(1))
################################################################################
# Train neural network
################################################################################
print("Training Neural Network")
# Print summary
model.summary()
# lossFunction = 'mean_absolute_error'
lossFunction = 'mean_squared_error'
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
################################################################################
# Export data
################################################################################
outDict = {}
outDict["testPredictList"] = testPredictList
outDict["testLabelList"] = testLabelList
outDict["testErrorLargerList"] = testErrorLargerList
outDict["testErrorSmallerList"] = testErrorSmallerList
outDict["testErrorList"] = testErrorList
outDict["lossList"] = lossListY
outDict["valLossList"] = valLossListY
# Save dataframe
with open(outputFileName, 'wb') as f:
	pickle.dump(outDict, f, pickle.HIGHEST_PROTOCOL)
f.close()
