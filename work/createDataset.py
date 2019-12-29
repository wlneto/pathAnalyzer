################################################################################
# Libraries
################################################################################
import pickle
import pandas as pd
import os
import pprint
from tensorflow.keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
################################################################################
# Config
################################################################################
trainDataPct = 0.6
validationDataPct = 0.2
targetCTDivisionFactor = 1000.0
featureTargetCTKey = "targetCT"
featurePathKey = "pathMap"
labelDividendKey = "delayOpt"
labelDivisorKey = "delayMap"
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
# Create dataset
################################################################################
dataset = pd.DataFrame(columns=["dataType", "databaseIdx", "featureTensor", "label"])
################################################################################
# Main program
################################################################################
# Shuffle database
print("Shuffling database")
database = database.sample(frac=1)
# Get largest path size to control padding and number of paths to control splits
largestPathSize = 0
numPaths = 0
for databaseIdx, databaseRow in database.iterrows():
	# Make sure label data is valid
	if (isinstance(databaseRow[labelDividendKey], float) or isinstance(databaseRow[labelDividendKey], int)) and (isinstance(databaseRow[labelDivisorKey], float) or isinstance(databaseRow[labelDivisorKey], int)):
		datasetPath = databaseRow[featurePathKey]
		largestPathSize = max(largestPathSize, len(datasetPath))
		numPaths = numPaths + 1
print("Found %d paths. Largest path has %d gates" % (numPaths, largestPathSize))
trainSplit = int(numPaths * trainDataPct)
validationSplit = trainSplit + int(numPaths * validationDataPct)
# Collect cell names to cellNameList
cellNameList = []
for path in database[featurePathKey].tolist():
	for cell in path:
		cellName = cell[0]
		if cellName not in cellNameList:
			cellNameList.append(cellName)
# Tokenize cell names using cellNameList
# TODO: Group cells by functionality
tokenizer = Tokenizer(filters='!"#$%&()*+,-./:;<=>?@[\\]^`{|}~\t\n')
tokenizer.fit_on_texts(cellNameList)
# Get vocabulary from Tokenizer
word_index = tokenizer.word_index
vocab_size=len(list(word_index.keys()))
print("Vocabulary (size %d) is:" % vocab_size)
pprint.pprint(word_index)
# Add features and labels to dataset
for databaseIdx, databaseRow in database.iterrows():
	# print("%d - %s" % (databaseIdx,databaseRow[labelDividendKey]))
	# Make sure label data is valid
	if (isinstance(databaseRow[labelDividendKey], float) or isinstance(databaseRow[labelDividendKey], int)) and (isinstance(databaseRow[labelDivisorKey], float) or isinstance(databaseRow[labelDivisorKey], int)):
		# Collect label
		label = float(databaseRow[labelDividendKey])/float(databaseRow[labelDivisorKey])
		# Create tensor
		featureTensor = []
		# Collect targetCT to add to tensors
		targetCT = float(databaseRow[featureTargetCTKey])/float(targetCTDivisionFactor)
		# Iterate through path to format data and add to tensor
		datasetPath = databaseRow[featurePathKey]
		for datasetPathCell in datasetPath:
			datasetPathCellName = datasetPathCell[0]
			datasetPathCellDrive = datasetPathCell[1]
			datasetPathCellDirection = datasetPathCell[2]
			datasetPathCellFanout = datasetPathCell[3]
			datasetPathCellLoad = datasetPathCell[4]
			datasetPathCellTranIn = datasetPathCell[5]
			datasetPathCellName = tokenizer.texts_to_sequences([datasetPathCellName])[0][0]
			datasetPathCellName = float(datasetPathCellName)/float(vocab_size)
			featureTensor.append([targetCT, datasetPathCellName, datasetPathCellDrive, datasetPathCellDirection, datasetPathCellFanout, datasetPathCellLoad])
		# Add padding to tensor
		for padIdx in range(len(featureTensor),largestPathSize):
			featureTensor.append([0, 0, 0, 0, 0, 0])
		# Add new row to dataset
		datasetIdx = dataset.index
		if (len(datasetIdx) == 0):
			datasetIdx = 0
		else:
			datasetIdx = max(dataset.index) + 1
		# Set data type
		if datasetIdx < trainSplit:
			dataType="Train"
		elif datasetIdx < validationSplit:
			dataType="Validation"
		else:
			dataType="Test"
		# Add to dataset
		dataset.loc[datasetIdx] = [dataType, databaseIdx, featureTensor, label]
	else:
		print("Ignoring path with no label: %d - %s" % (databaseIdx,databaseRow[labelDividendKey]))

# Save dataframe
with open(datasetFileName, 'wb') as f:
	pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
f.close()
