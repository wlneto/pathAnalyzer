################################################################################
# Libraries
################################################################################
import pickle
# import pandas as pd
import os
import sys
sys.path.append(os.path.realpath("../src"))
from PathDatabase import PathDatabase
from PathDataset import PathDataset
################################################################################
# Config
################################################################################
if len(sys.argv) != 7:
	raise RuntimeError("Missing parameters. Read %s" % sys.argv[1:])
databaseFileName = str(sys.argv[1])
datasetFileName = str(sys.argv[2])
# 0 for all paths
numSamples = 0
critPathTh = 0.9
targetCTDivisionFactor = 1000.0
fanoutDivisionFactor = 100.0
pathKey = PathDatabase.synGenPathKey
delayKey = PathDatabase.placeAndRouteDelayKey
trainPct=float(sys.argv[3])
valPct=float(sys.argv[4])
testPct=float(sys.argv[5])
largestPathSize=int(sys.argv[6])
strategy=int(sys.argv[7])
print("##############################################")
print("Creating dataset with configs:")
print("databaseFileName: %s" % databaseFileName)
print("datasetFileName:  %s" % datasetFileName)
print("trainPct:         %f" % trainPct)
print("valPct:           %f" % valPct)
print("testPct:          %f" % testPct)
print("largestPathSize:  %d" % largestPathSize)
print("strategy:         %d" % strategy)
print("##############################################")
################################################################################
# Load Database
################################################################################
print("Loading database")
if os.path.exists(databaseFileName):
	with open(databaseFileName, 'rb') as f:
		database = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (databaseFileName))
# print("Printing database")
# print(database.tabulate())
print("Cleaning database")
removedRows=0
removedRows+=database.clean(pathKey=PathDatabase.synGenPathKey)
# removedRows+=database.clean(pathKey=PathDatabase.synMapPathKey)
# removedRows+=database.clean(pathKey=PathDatabase.synOptPathKey)
# removedRows+=database.clean(pathKey=PathDatabase.placeAndRoutePathKey)
print("Removed %d rows" % removedRows)
# print("Printing database")
# print(database.tabulate())
with open("clean_"+databaseFileName, 'wb') as f:
	pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)
f.close()
################################################################################
# Main program
################################################################################
pathDatabase = database
print("Creating dataset")
# Get largest path size to control padding and number of paths to control splits
if(largestPathSize == 0):
	for databaseIdx, databaseRow in pathDatabase.database.iterrows():
		# Make sure label data is valid
		if (isinstance(databaseRow[delayKey], float) or isinstance(databaseRow[delayKey], int)):
			datasetPath = databaseRow[pathKey]
			largestPathSize = max(largestPathSize, len(datasetPath))
# Create dataset
dataset = PathDataset(pathSize = largestPathSize, strategy = strategy)
print("Adding data to dataset with largest path = %d" % largestPathSize)
dataset.add(pathDatabase, numSamples=numSamples, critPathTh=critPathTh, pathKey=pathKey, delayKey=delayKey, targetCTDivisionFactor=targetCTDivisionFactor, fanoutDivisionFactor=fanoutDivisionFactor)
print("Splitting dataset")
dataset.split(trainPct=trainPct, valPct=valPct, testPct=testPct)
# print("Plotting dataset")
# dataset.plotTensorToFeature()
# print("Printing dataset")
# print(dataset.tabulate())
# Save dataframe
with open(datasetFileName, 'wb') as f:
	pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
f.close()
