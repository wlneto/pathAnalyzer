################################################################################
# Libraries
################################################################################
import os
import sys
import re
import pickle
sys.path.append(os.path.realpath("../src"))
from PathDatabase import PathDatabase
################################################################################
# Config
################################################################################
# databaseFileName = "aesDatabase.pkl"
# databaseFileName = "adderDatabase.pkl"
databaseFileName = "riscvDatabase.pkl"
# databaseFileName = "fullDatabase.pkl"
################################################################################
# Main program
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
print("Plotting database")
database.plot()
