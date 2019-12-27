# import pickle
import csv
import pandas as pd
import re

cktList = ["ethernet_218"]
csvFileDir = "../data"
csvFileSuffixGen = "_timing_by_pairs.csv"
csvFileSuffixMap = "_mapped_timing_by_pairs.csv"
csvFileSuffixOpt = "_opt_timing_by_pairs.csv"
cellNameRmStrListGen = ["unmapped_"]
pathMinSize = 2
pathMaxSize = 1000

df = pd.DataFrame(columns=["circuit", "startpoint", "endpoint", "startDirection", "endDirection", "path", "delayGen", "delayMap", "delayOpt"])
dfIdx = 0

# Function to collect the information of a cell with row = [Rise/Fall, CellName, Fanout, Load, PropDelay, TranDelay]
# Returns tuple as cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay, tranOut
def getCellInfo(row, tranIn, cellNameRmStrList, cellDrivingStregthRegexp = ""):
	cellName = None
	cellDrive = None
	direction = None
	tranIn = None
	load = None
	fanout = None
	tranOut = None
	delay = None
	tranOut = None
	# Ignore gates w/ 0 delay (endpoints)
	if not(int(row[4]) == 0 or str(row[4]) == "-"):
		# Rise/Fall
		if row[0] == "F":
			direction = 0
		else:
			direction = 1
		# Get cell name and clean
		cellName = row[1]
		for cellNameRmStr in cellNameRmStrList:
			cellName = re.sub(cellNameRmStr, '', cellName)
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
	return cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay, tranOut

for ckt in cktList:
	print("Reading circuit %s" % ckt)
	csvPath = csvFileDir+"/"+ckt+csvFileSuffixGen
	print("  Reading generic synthesis file %s" % csvPath)
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
				if pathDelay is not None:
					# Ignore empty paths
					if (len(path) < pathMinSize) or (len(path) > pathMaxSize):
						print("    Ignoring path because it is out of path size filter(%s) %s" % (pathDelay,path))
					# Otherwise add to dataset
					else:
						df = pd.DataFrame(columns=["circuit", "startpoint", "endpoint", "startDirection", "endDirection", "pathGen", "pathMap", "pathOpt", "delayGen", "delayMap", "delayOpt"])
						startDirection = path[0][2]
						endDirection = path[-1][2]
						df.loc[dfIdx] = [ckt, startpoint, endpoint, startDirection, endDirection, path, [], [], pathDelay, -1.0, -1.0]
						dfIdx = dfIdx + 1
				startpoint = str(row[1])
				endpoint = str(row[2])
				pathDelay = float(row[3])
				# print("    Found new path from %s to %s with delay of %f" % (startpoint, endpoint, pathDelay))
				path = []
				tranIn = None
			# If inside a path
			else:
				# This is probably an error
				if pathDelay is None:
					raise RuntimeError("Found invalid path!!")
				# Otherwise add to path
				else:
					cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay, tranOut = getCellInfo(row=row, tranIn=tranIn, cellNameRmStrList=cellNameRmStrListGen, cellDrivingStregthRegexp="")
					if cellName is not None:
						path.append([str(cellName), float(cellDrive), int(direction), float(load), int(fanout), float(tranOut)])
					# Prepare for next iteration
					tranIn = tranOut

print(df)
