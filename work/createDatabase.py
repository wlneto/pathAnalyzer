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
csvFileDir = "../data"
# cktList = ["_debug_file_dont_use_218"]
cktList = ["aes_250", "aes_350", "aes_450", "aes_650", "aes_750", "aes_850"]
collectSynGen = True
collectSynMap = True
collectSynOpt = True
collectPnR = True
cktNameAndCTRegexp = "(.+)_([0-9]+)"
cellDrivingStregthRegexpGen = ""
cellDrivingStregthRegexpMap = "(.+)x([0-9p]+)"
cellDrivingStregthRegexpOpt = "(.+)x([0-9p]+)"
cellDrivingStregthRegexpPnR = "(.+)x([0-9p]+)"
csvFileSuffixGen = "_generic_timing_by_pairs.csv"
csvFileSuffixMap = "_mapped_timing_by_pairs.csv"
csvFileSuffixOpt = "_opt_timing_by_pairs.csv"
csvFileSuffixPnR = "_timing_PR.csv"
cellNameRmRegexpListGen = ["unmapped_"]
cellNameRmRegexpListMap = ["_ASAP7_75t_R"]
cellNameRmRegexpListOpt = ["_ASAP7_75t_R"]
cellNameRmRegexpListPnR = ["_ASAP7_75t_R"]
startpointRmRegexpList = ["/.*"]
endpointRmRegexpList = ["/.*"]
pathMinSize = 1
pathMaxSize = 100000
databaseFileName = "aesDatabase.pkl"
################################################################################
# Main program
################################################################################
pathDatabase = PathDatabase()
for ckt in cktList:
	cktNameAndCT = re.match(cktNameAndCTRegexp, ckt)
	if cktNameAndCT:
		cktName = cktNameAndCT.group(1)
		targetCT = float(cktNameAndCT.group(2))
	else:
		raise RuntimeError("Reading ckt %s" % (ckt))
	print("################################################################################")
	print("Reading circuit %s with target cycle time %s" % (cktName, str(targetCT)))
	print("################################################################################")
	# syn Gen data
	if collectSynGen:
		csvPath = csvFileDir+"/"+ckt+csvFileSuffixGen
		print("## Reading generic synthesis file %s" % csvPath)
		pathDatabase.readCktFile(csvPath=csvPath,
		                         cktName=cktName,
		                         targetCT=targetCT,
		                         pathType=pathDatabase.synGenPathTypeLabel,
		                         pathMinSize=pathMinSize,
		                         pathMaxSize=pathMaxSize,
		                         cellDrivingStregthRegexp=cellDrivingStregthRegexpGen,
		                         startpointRmRegexpList=startpointRmRegexpList,
		                         endpointRmRegexpList=endpointRmRegexpList,
		                         cellNameRmRegexpList=cellNameRmRegexpListGen)
		# Save dataframe
		with open(databaseFileName, 'wb') as f:
			pickle.dump(pathDatabase, f, pickle.HIGHEST_PROTOCOL)
		f.close()
	# Syn map data
	if collectSynMap:
		csvPath = csvFileDir+"/"+ckt+csvFileSuffixMap
		print("## Reading mapped synthesis file %s" % csvPath)
		pathDatabase.readCktFile(csvPath=csvPath,
		                         cktName=cktName,
		                         targetCT=targetCT,
		                         pathType=pathDatabase.synMapPathTypeLabel,
		                         pathMinSize=pathMinSize,
		                         pathMaxSize=pathMaxSize,
		                         cellDrivingStregthRegexp=cellDrivingStregthRegexpMap,
		                         startpointRmRegexpList=startpointRmRegexpList,
		                         endpointRmRegexpList=endpointRmRegexpList,
		                         cellNameRmRegexpList=cellNameRmRegexpListMap)
		# Save dataframe
		with open(databaseFileName, 'wb') as f:
			pickle.dump(pathDatabase, f, pickle.HIGHEST_PROTOCOL)
		f.close()
	# Syn Opt Data
	if collectSynOpt:
		csvPath = csvFileDir+"/"+ckt+csvFileSuffixOpt
		print("## Reading optimized synthesis file %s" % csvPath)
		pathDatabase.readCktFile(csvPath=csvPath,
		                         cktName=cktName,
		                         targetCT=targetCT,
		                         pathType=pathDatabase.synOptPathTypeLabel,
		                         pathMinSize=pathMinSize,
		                         pathMaxSize=pathMaxSize,
		                         cellDrivingStregthRegexp=cellDrivingStregthRegexpOpt,
		                         startpointRmRegexpList=startpointRmRegexpList,
		                         endpointRmRegexpList=endpointRmRegexpList,
		                         cellNameRmRegexpList=cellNameRmRegexpListOpt)
		# Save dataframe
		with open(databaseFileName, 'wb') as f:
			pickle.dump(pathDatabase, f, pickle.HIGHEST_PROTOCOL)
		f.close()
	# Place and Route data
	if collectPnR:
		csvPath = csvFileDir+"/"+ckt+csvFileSuffixPnR
		print("## Reading optimized synthesis file %s" % csvPath)
		pathDatabase.readCktFile(csvPath=csvPath,
		                         cktName=cktName,
		                         targetCT=targetCT,
		                         pathType=pathDatabase.placeAndRoutePathTypeLabel,
		                         pathMinSize=pathMinSize,
		                         pathMaxSize=pathMaxSize,
		                         cellDrivingStregthRegexp=cellDrivingStregthRegexpPnR,
		                         startpointRmRegexpList=startpointRmRegexpList,
		                         endpointRmRegexpList=endpointRmRegexpList,
		                         cellNameRmRegexpList=cellNameRmRegexpListPnR)
		# Save dataframe
		with open(databaseFileName, 'wb') as f:
			pickle.dump(pathDatabase, f, pickle.HIGHEST_PROTOCOL)
		f.close()

# print(pathDatabase.tabulate())
