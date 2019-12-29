################################################################################
# Libraries
################################################################################
import pickle
import csv
import pandas as pd
# from tabulate import tabulate
import re
################################################################################
# Config
################################################################################
csvFileDir = "../data"
cktList = ["ethernet_218"]
cktNameAndCTRegexp = "(.+)_([0-9]+)"
cellDrivingStregthRegexpGen = ""
cellDrivingStregthRegexpMap = "(.+)x([0-9p]+)"
cellDrivingStregthRegexpOpt = "(.+)x([0-9p]+)"
cellDrivingStregthRegexpPnR = "(.+)x([0-9p]+)"
csvFileSuffixGen = "_timing_by_pairs.csv"
csvFileSuffixMap = "_mapped_timing_by_pairs.csv"
csvFileSuffixOpt = "_opt_timing_by_pairs.csv"
csvFileSuffixPnR = "_timing_PR.csv"
cellNameRmRegexpListGen = ["unmapped_"]
cellNameRmRegexpListMap = ["_ASAP7_75t_R"]
cellNameRmRegexpListOpt = ["_ASAP7_75t_R"]
cellNameRmRegexpListPnR = ["_ASAP7_75t_R"]
startpointRmRegexpList = ["/.*"]
endpointRmRegexpList = ["/.*"]
pathMinSize = 2
pathMaxSize = 1000
databaseFileName = "database.pkl"
################################################################################
# Database setup
################################################################################
df = pd.DataFrame(columns=["circuit", "startpoint", "endpoint", "targetCT", "pathGen", "pathMap", "pathOpt", "pathPnR", "delayGen", "delayMap", "delayOpt", "delayPnR"])
# dfIdx = 0
################################################################################
# Functions
################################################################################
# Function to collect the information of a cell with row = [Rise/Fall, CellName, Fanout, Load, PropDelay, TranDelay]
# Returns tuple as cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay
def getCellInfo(row, tranIn, cellNameRmRegexpList, cellDrivingStregthRegexp = ""):
	# Initialize return values
	cellName = None
	cellDrive = None
	direction = None
	load = None
	fanout = None
	tranOut = None
	delay = None
	# Ignore gates w/ 0 delay (endpoints)
	if not(int(float(row[4])) == 0 or str(row[4]) == "-" or row[2] == ""):
		# Rise/Fall
		if row[0] == "F" or row[0] == "v":
			direction = -1
		else:
			direction = 1
		# Get cell name and clean
		cellName = row[1]
		for cellNameRmRegexp in cellNameRmRegexpList:
			cellName = re.sub(cellNameRmRegexp, '', cellName)
		# Initialize driving strength
		cellDrive = 0.0
		# Split name and driving strength
		if cellDrivingStregthRegexp != "":
			nameDrive = re.match(cellDrivingStregthRegexp, cellName)
			if nameDrive:
				cellName = nameDrive.group(1)
				cellDrive = nameDrive.group(2)
				cellDrive = float(re.sub('p', '.', cellDrive))
			# If regexp didnt capture driving strength
			else:
				raise RuntimeError("ERROR! No match for cell %s with regexp %s" % (cellName, cellDrivingStregthRegexp))
		# Fanout
		fanout = float(row[2])
		# Load
		load = float(row[3])
		# delay
		delay = float(row[4])
		# Output transition
		tranOut = float(row[5])
	return cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay

# Adds data to the dataframe. Expects the following format for keys in df:
# ["circuit", "startpoint", "endpoint", "targetCT", "pathGen", "pathMap", "pathOpt", "delayGen", "delayMap", "delayOpt"]
def addToDataframe(df, pathMinSize, pathMaxSize, createRow,
                   cktName, targetCT, startpoint, endpoint, pathType, path, pathDelay):
	# Filter by min max path size
	if (len(path) < pathMinSize) or (len(path) > pathMaxSize):
		print("    Ignoring path of circuit %s from %s to %s (type %s) because it is out of path size filter (%d) %s" % (cktName, startpoint, endpoint, pathType, len(path), path))
	# Otherwise add to dataset
	else:
		# endDirection = path[-1][2]
		# Create row if needed
		if createRow:
			# If not in dataframe add it
			if not ((df["circuit"] == cktName) & (df["startpoint"] == startpoint) & (df["endpoint"] == endpoint)).any():
				dfIdx = df.index
				if (len(dfIdx) == 0):
					dfIdx = 0
				else:
					dfIdx = max(df.index) + 1
				df.loc[dfIdx] = [cktName, startpoint, endpoint, targetCT, [], [], [], [], None, None, None, None]
		# Check if current cktName, startpoint and endpoint exists in the dataframe
		dfIdxMatchList = df.index[(df["circuit"] == cktName) & (df["startpoint"] == startpoint) & (df["endpoint"] == endpoint)].tolist()
		# If not in dataframe
		if len(dfIdxMatchList) < 1:
			print("Could not find path of circuit %s from %s to %s (type %s) in the dataframe" % (cktName, startpoint, endpoint, pathType))
		# If multiple matches in dataframe
		elif len(dfIdxMatchList) > 1:
			raise RuntimeError("Found multiple matches of path of circuit %s from %s to %s (type %s) in the dataframe" % (cktName, startpoint, endpoint, pathType))
		# If exactly one match in dataframe
		else:
			# Add generic synthesis data
			if pathType == "gen":
				df.at[dfIdxMatchList[0], "pathGen"] = path
				df.at[dfIdxMatchList[0], "delayGen"] = pathDelay
			# Add mapped synthesis data
			elif pathType == "map":
				df.at[dfIdxMatchList[0], "pathMap"] = path
				df.at[dfIdxMatchList[0], "delayMap"] = pathDelay
			# Add optimization synthesis data
			elif pathType == "opt":
				df.at[dfIdxMatchList[0], "pathOpt"] = path
				df.at[dfIdxMatchList[0], "delayOpt"] = pathDelay
			# Add place and route data
			elif pathType == "pnr":
				df.at[dfIdxMatchList[0], "pathPnR"] = path
				df.at[dfIdxMatchList[0], "delayPnR"] = pathDelay
			else:
				raise RuntimeError("Found invalid option when adding circuit to dataframe!!")

# Reads a circuit file in CSV with path information. Expects the following
# format:
# Path 0, startpoint, endpoint, delay
# direction,gateName,fanout,outputLoad,PropagationDelay,TransitionDelay
# ...
# direction,gateName,fanout,outputLoad,PropagationDelay,TransitionDelay
# Path 1, startpoint, endpoint, delay
# direction,gateName,fanout,outputLoad,PropagationDelay,TransitionDelay
# ...
# direction,gateName,fanout,outputLoad,PropagationDelay,TransitionDelay
# ...
#
# Paths are created as:
# [cellName, cellDrive, direction, load, fanout, tranIn]
# Start and endpoints may be ports or cell pins
def readCktFile(df, csvPath, targetCT, cellDrivingStregthRegexp,
                startpointRmRegexpList, endpointRmRegexpList,
                cellNameRmRegexpList, pathMinSize, pathMaxSize, createRow,
                cktName, pathType):
	# Read CSV file
	with open(csvPath, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		# Initialize control variable that holds the label of a path
		pathDelay = None
		path = []
		startpoint = None
		endpoint = None
		for row in reader:
			# If new path found
			if re.match("Path [0-9]+", row[0]):
				# If not first path to be found, add info
				if pathDelay is not None:
					addToDataframe(df=df, pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
					               createRow=createRow, cktName=cktName, targetCT=targetCT,
					               startpoint=startpoint, endpoint=endpoint,
					               pathType=pathType,
					               path=path, pathDelay=pathDelay)
				# Collect new startpoint, endpoint and delay data
				startpoint = str(row[1])
				for startpointRmRegexp in startpointRmRegexpList:
					startpoint = re.sub(startpointRmRegexp, '', startpoint)
				endpoint = str(row[2])
				for endpointRmRegexp in endpointRmRegexpList:
					endpoint = re.sub(endpointRmRegexp, '', endpoint)
				pathDelay = float(row[3])
				# print("    Found new path from %s to %s with delay of %f" % (startpoint, endpoint, pathDelay))
				path = []
				tranIn = 0
			# If inside a path
			else:
				# This is probably an error
				if pathDelay is None:
					raise RuntimeError("Found invalid path!!")
				# Otherwise add to path
				else:
					cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay = getCellInfo(row=row, tranIn=tranIn, cellNameRmRegexpList=cellNameRmRegexpList, cellDrivingStregthRegexp=cellDrivingStregthRegexp)
					if not(isinstance(tranIn, float) or isinstance(tranIn, int)):
						tranIn = 0.0
					if cellName is not None:
						try:
							# print("Adding cellName=%s, cellDrive=%s, direction=%s, fanout=%s, load=%s, tranIn=%s" % (str(cellName), str(cellDrive), str(direction), str(fanout), str(load), str(tranIn)))
							path.append([str(cellName), float(cellDrive), int(direction), int(fanout), float(load), float(tranIn)])
						except:
							raise RuntimeError("Error when adding cellName=%s, cellDrive=%s, direction=%s, fanout=%s, load=%s, tranIn=%s" % (str(cellName), str(cellDrive), str(direction), str(fanout), str(load), str(tranIn)))
					# Prepare for next iteration
					tranIn = tranOut
	# If still one last path to add
	if pathDelay is not None:
		addToDataframe(df=df, pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
		               createRow=createRow, cktName=cktName, targetCT=targetCT,
		               startpoint=startpoint, endpoint=endpoint,
		               pathType=pathType,
		               path=path, pathDelay=pathDelay)

################################################################################
# Main program
################################################################################
for ckt in cktList:
	cktNameAndCT = re.match(cktNameAndCTRegexp, ckt)
	if cktNameAndCT:
		cktName = cktNameAndCT.group(1)
		targetCT = cktNameAndCT.group(2)
	print("Reading circuit %s with target cycle time %s" % (cktName, str(targetCT)))
	csvPath = csvFileDir+"/"+ckt+csvFileSuffixGen
	print("  Reading generic synthesis file %s" % csvPath)
	readCktFile(df=df, csvPath=csvPath, targetCT=targetCT, cellDrivingStregthRegexp=cellDrivingStregthRegexpGen,
	            startpointRmRegexpList=startpointRmRegexpList, endpointRmRegexpList=endpointRmRegexpList,
	            cellNameRmRegexpList=cellNameRmRegexpListGen,
	            pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
	            createRow=True, cktName=cktName, pathType="gen")
	csvPath = csvFileDir+"/"+ckt+csvFileSuffixMap
	print("  Reading mapped synthesis file %s" % csvPath)
	readCktFile(df=df, csvPath=csvPath, targetCT=targetCT, cellDrivingStregthRegexp=cellDrivingStregthRegexpMap,
	            startpointRmRegexpList=startpointRmRegexpList, endpointRmRegexpList=endpointRmRegexpList,
	            cellNameRmRegexpList=cellNameRmRegexpListMap,
	            pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
	            createRow=False, cktName=cktName, pathType="map")
	csvPath = csvFileDir+"/"+ckt+csvFileSuffixOpt
	print("  Reading optimized synthesis file %s" % csvPath)
	readCktFile(df=df, csvPath=csvPath, targetCT=targetCT, cellDrivingStregthRegexp=cellDrivingStregthRegexpOpt,
	            startpointRmRegexpList=startpointRmRegexpList, endpointRmRegexpList=endpointRmRegexpList,
	            cellNameRmRegexpList=cellNameRmRegexpListOpt,
	            pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
	            createRow=False, cktName=cktName, pathType="opt")
	csvPath = csvFileDir+"/"+ckt+csvFileSuffixPnR
	print("  Reading optimized synthesis file %s" % csvPath)
	readCktFile(df=df, csvPath=csvPath, targetCT=targetCT, cellDrivingStregthRegexp=cellDrivingStregthRegexpPnR,
	            startpointRmRegexpList=startpointRmRegexpList, endpointRmRegexpList=endpointRmRegexpList,
	            cellNameRmRegexpList=cellNameRmRegexpListPnR,
	            pathMinSize=pathMinSize, pathMaxSize=pathMaxSize,
	            createRow=False, cktName=cktName, pathType="pnr")

# print(tabulate(df, headers='keys', tablefmt='psql'))
# Save dataframe
with open(databaseFileName, 'wb') as f:
	pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
f.close()
