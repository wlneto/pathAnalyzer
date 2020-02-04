################################################################################
# Libraries
################################################################################
import pickle
import numpy as np
from tabulate import tabulate
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
dataTypeKey = "dataType"
featureTensorKey = "featureTensor"
labelKey = "label"
trainDatasetFileName = "synGenOnlyLoadTrainDataset.pkl"
testDatasetFileName = "synGenOnlyLoadTestDataset.pkl"
outlierErrorThreshold = 0.1
outlierList = []
checkpointPath = "neuralNetworkTraining/nn~{epoch:04d}.ckpt"
checkpointFreq = 20
################################################################################
# Load Dataset
################################################################################
print("Collecting testDataset")
if os.path.exists(testDatasetFileName):
	with open(testDatasetFileName, 'rb') as f:
		testDataset = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (testDatasetFileName))
print(tabulate(testDataset.dataset, headers='keys', tablefmt='psql'))
################################################################################
# Prepare data
################################################################################
print("Collecting test data")
testDatasetDF=testDataset.dataset
testFeatureList = []
testLabelList = []
startpointList = []
endpointList = []
for testDatasetIdx, testDatasetRow in testDatasetDF[testDatasetDF[PathDataset.dataTypeKey] == PathDataset.testDataLabel].iterrows():
	testFeatureList.append(testDatasetRow[PathDataset.featureTensorKey])
	testLabelList.append(testDatasetRow[PathDataset.labelKey])
	startpointList.append(testDatasetRow["startpoint"])
	endpointList.append(testDatasetRow["endpoint"])
testSetSize = len(testLabelList)
print("  Test set size = %d" % testSetSize)
print("Preparing Numpy Arrays")
maxPathSize = 25
cellFeatureSize = len(testFeatureList[0][0])
featureTensorShape = (maxPathSize, cellFeatureSize, 1)
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
model.add(tf.keras.layers.Conv2D(16, (2,1), activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Conv2D(16, (2,1), activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(8, activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
model.add(tf.keras.layers.Dense(8, activation='relu'))
model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(32, activation='relu'))
# model.add(tf.keras.layers.Dropout(0.1))
# model.add(tf.keras.layers.Dense(512, activation='relu'))
# model.add(tf.keras.layers.Dense(8, activation='relu'))
# model.add(tf.keras.layers.Dense(1024, activation='relu'))
# model.add(tf.keras.layers.Dense(1))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
################################################################################
# Restore Neural Network
################################################################################
print("Restoring Neural Network")
# Print summary
model.summary()
# Checkpoint
checkpointDir = os.path.dirname(checkpointPath)
lastCheckpoint = tf.train.latest_checkpoint(checkpointDir)
model.load_weights(lastCheckpoint)
################################################################################
# Run for input fetures
################################################################################
print("Predicting constraints")
testPredictList = model.predict(testFeatureList)
print("  Collected %d predictions" % len(testPredictList))
testPredictList = testPredictList.reshape(len(testPredictList))
fig = go.Figure(data=[go.Histogram(x=testPredictList)])
fig.update_layout(title="Predictions")
fig.show()
################################################################################
# Generate SDC
################################################################################
f = open("nn_optimize.sdc", "w")
f2 = open("nn_revert.sdc", "w")
for testPredict, startpoint, endpoint in zip(testPredictList, startpointList, endpointList):
	if testPredict > 0.5:
		f.write("set_max_delay 0 -from %s -to %s\n" % (startpoint, endpoint))
		f2.write("set_max_delay 675 -from %s -to %s\n" % (startpoint, endpoint))
f.close()
f2.close()
