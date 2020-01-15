################################################################################
# Libraries
################################################################################
import pickle
# import pandas as pd
import os
import sys
sys.path.append(os.path.realpath("../src"))
from PathDataset import PathDataset
################################################################################
# Config
################################################################################
# -1 for all paths
numPathsToAdd = 30000
trainPathCount = 10000
validationPathCount = 5000
targetCTDivisionFactor = 1000.0
fanoutDivisionFactor = 100.0
# delayDivisionFactor = 100.0
dataTypeTrainLabel = "Train"
dataTypeValidationLabel = "Validation"
dataTypeTestLabel = "Test"
dataTypeUnassignedLabel = "Unassigned"
featureTargetCTKey = "targetCT"
dataTypeKey = "dataType"
featurePathKey = "pathGen"
labelDelayKey = "delayOpt"
databaseFileName = "database.pkl"
datasetFileName = "dataset.pkl"
################################################################################
# Load Database
################################################################################
if os.path.exists(databaseFileName):
	with open(databaseFileName, 'rb') as f:
		database = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (databaseFileName))
# print(tabulate(database, headers='keys', tablefmt='psql'))
################################################################################
# Main program
################################################################################
dataset = PathDataset()
dataset.add(database, numSamples=10)
exit()
# Shuffle database
print("Shuffling database")
database = database.sample(frac=1)
# Get largest path size to control padding and number of paths to control splits
largestPathSize = 0
numPaths = 0
for databaseIdx, databaseRow in database.iterrows():
	# Make sure label data is valid
	if (isinstance(databaseRow[labelDelayKey], float) or isinstance(databaseRow[labelDelayKey], int)):
		datasetPath = databaseRow[featurePathKey]
		largestPathSize = max(largestPathSize, len(datasetPath))
		numPaths = numPaths + 1
print("Found %d paths. Largest path has %d gates" % (numPaths, largestPathSize))
# ## Using TOkenizer
# # Collect cell names to cellNameList
# cellNameList = []
# for path in database[featurePathKey].tolist():
# 	for cell in path:
# 		cellName = cell[0]
# 		if cellName not in cellNameList:
# 			cellNameList.append(cellName)
# # Tokenize cell names using cellNameList
# # TODO: Group cells by functionality
# tokenizer = Tokenizer(filters='!"#$%&()*+,-./:;<=>?@[\\]^`{|}~\t\n')
# tokenizer.fit_on_texts(cellNameList)
# # Get vocabulary from Tokenizer
# word_index = tokenizer.word_index
# vocab_size=len(list(word_index.keys()))
# print("Vocabulary (size %d) is:" % vocab_size)
# pprint.pprint(word_index)
cellMap = {"not" : 0, "nand2" : 1, "nor2" : 1, "and2" : 2, "or2" : 2, "complex2" : 3, "d_flop" : 4}
# Add features and labels to dataset
if numPathsToAdd < 0 or numPathsToAdd > numPaths:
	numPathsToAdd = numPaths
print("Adding %d paths to dataset" % numPathsToAdd)
for databaseIdx, databaseRow in database.iterrows():
	# print("%d - %s" % (databaseIdx,databaseRow[labelDelayKey]))
	# Make sure label data is valid
	if (isinstance(databaseRow[labelDelayKey], float) or isinstance(databaseRow[labelDelayKey], int)):
		# Collect targetCT to add to tensors
		targetCT = float(databaseRow[featureTargetCTKey])/float(targetCTDivisionFactor)
		# Collect label
		label = float(databaseRow[labelDelayKey])/float(databaseRow[featureTargetCTKey])
		# Create tensor
		featureTensor = []
		# Iterate through path to format data and add to tensor
		datasetPath = databaseRow[featurePathKey]
		for datasetPathCell in datasetPath:
			datasetPathCellName = datasetPathCell[0]
			datasetPathCellDrive = datasetPathCell[1]
			datasetPathCellDirection = datasetPathCell[2]
			datasetPathCellFanout = datasetPathCell[3]
			datasetPathCellLoad = datasetPathCell[4]
			datasetPathCellTranIn = datasetPathCell[5]
			# datasetPathCellName = tokenizer.texts_to_sequences([datasetPathCellName])[0][0]
			# datasetPathCellName = float(datasetPathCellName)/float(vocab_size)
			datasetPathCellName = cellMap[datasetPathCellName]
			datasetPathCellFanout = datasetPathCellFanout / fanoutDivisionFactor
			# featureTensor.append([targetCT, datasetPathCellName, datasetPathCellDrive, datasetPathCellDirection, datasetPathCellFanout, datasetPathCellLoad])
			featureTensor.append([targetCT, datasetPathCellName, datasetPathCellDirection, datasetPathCellFanout])
		# Add padding to tensor
		for padIdx in range(len(featureTensor),largestPathSize):
			featureTensor.append(len(featureTensor[0])*[0])
		# Add new row to dataset
		datasetIdx = dataset.index
		if (len(datasetIdx) == 0):
			datasetIdx = 0
		else:
			datasetIdx = max(dataset.index) + 1
		# Add to dataset
		dataset.loc[datasetIdx] = [dataTypeUnassignedLabel, databaseIdx, featureTensor, label]
		if datasetIdx % 1000 == 0:
			print("Current path # is %d of %d" % (datasetIdx,numPathsToAdd))
		# Exit when added enough paths
		if datasetIdx >= numPathsToAdd-1:
			break
	# else:
	# 	print("Ignoring path with no label: %d - %s" % (databaseIdx,databaseRow[labelDelayKey]))
# Label paths to split dataset
# trainPathCount = int(numPathsToAdd * trainDataPct)
# validationPathCount = int(numPathsToAdd * validationDataPct)
# testPathCount = int(numPathsToAdd * testDataPct)
trainSplit = trainPathCount
validationSplit = trainSplit + validationPathCount
testPathCount = numPathsToAdd - trainPathCount - validationPathCount
print("Labeling paths %d Training, %d Validation and %d Test" % (trainPathCount, validationPathCount, testPathCount))
for datasetIdx, datasetRow in dataset.iterrows():
	# Set data type
	if datasetIdx < trainSplit:
		dataType=dataTypeTrainLabel
	elif datasetIdx < validationSplit:
		dataType=dataTypeValidationLabel
	else:
		dataType=dataTypeTestLabel
	dataset.at[datasetIdx, dataTypeKey] = dataType
# Save dataframe
with open(datasetFileName, 'wb') as f:
	pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
f.close()
