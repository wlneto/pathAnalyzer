################################################################################
# Libraries
################################################################################
import os
import sys
import re
import pickle
import pandas as pd
sys.path.append(os.path.realpath("../src"))
from PathDatabase import PathDatabase
################################################################################
# Config
################################################################################
csvFileDir = "../data"
databaseInputFileNameList = sys.argv[2:]
databaseFileName = sys.argv[1]
################################################################################
# Main program
################################################################################
print("Loading input database list")
# Load databases
databaseList = []
for databaseInputFileName in databaseInputFileNameList:
	print("  Loading %s" % databaseInputFileName)
	if os.path.exists(databaseInputFileName):
		with open(databaseInputFileName, 'rb') as f:
			pathDatabase = pickle.load(f)
			databaseList.append(pathDatabase.database)
		f.close()
	else:
		raise RuntimeError("ERROR! Couldn't find file %s" % (databaseFileName))
# Create dataframe from concatenation
fullDatabase = pd.concat(databaseList, ignore_index=True)
print("Creating full path database object")
fullPathDatabase = PathDatabase(database = fullDatabase)
# # Print
# print(fullPathDatabase.tabulate())
# Save path database
with open(databaseFileName, 'wb') as f:
	pickle.dump(fullPathDatabase, f, pickle.HIGHEST_PROTOCOL)
f.close()
