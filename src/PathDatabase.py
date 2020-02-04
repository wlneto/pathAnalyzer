## \file PathDatabase.py
#  \brief Class ..
#
# Aaa
#
# Revision | Author            | Date     | Comment
#:---------|:------------------|:---------|:----------------
# 1.0      | Matheus T. M.     | 12/31/19 | Initial version
# 1.1      | Matheus T. M.     | 01/17/20 | Adding option to clean database
# 1.2      | Matheus T. M.     | 01/18/20 | Fixing bug in clean method
# 1.3      | Matheus T. M.     | 01/26/20 | Updating methods to support mapped gates data
# 1.4      | Matheus T. M.     | 01/28/20 | Adding plot methods
# 1.5      | Matheus T. M.     | 02/03/20 | Adding full path info with cellName, cellDrive, direction, fanout, load, tranIn, delay, tranOut
#

import gc
import csv
import re
import pandas as pd
from tabulate import tabulate
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PathDatabase(object):
	# Keys
	cktNameKey                = "cktName"
	startpointKey             = "startpoint"
	endpointKey               = "endpoint"
	targetCycleTimeKey        = "targetCycleTime"
	synGenPathKey             = "synGenPath"
	synMapPathKey             = "synMapPath"
	synOptPathKey             = "synOptPath"
	placeAndRoutePathKey      = "placeAndRoutePath"
	synGenDelayKey            = "synGenDelay"
	synMapDelayKey            = "synMapDelay"
	synOptDelayKey            = "synOptDelay"
	placeAndRouteDelayKey     = "placeAndRouteDelay"
	# Labels
	synGenPathTypeLabel         = "synGen"
	synMapPathTypeLabel         = "synMap"
	synOptPathTypeLabel         = "synOpt"
	placeAndRoutePathTypeLabel  = "placeAndRoute"
	pathTypeList = [synGenPathTypeLabel, synMapPathTypeLabel, synOptPathTypeLabel, placeAndRoutePathTypeLabel]

	## Constructor
	#
	# \param self Instance of PathDatabase class.
	# \param database Optional Dataframe to initialize PathDatabase
	def __init__(self, database=None):
		super(PathDatabase, self).__init__()

		if database is None:
			self.__database = pd.DataFrame(columns=[PathDatabase.cktNameKey,
			                                        PathDatabase.startpointKey,
			                                        PathDatabase.endpointKey,
			                                        PathDatabase.targetCycleTimeKey,
			                                        PathDatabase.synGenPathKey,
			                                        PathDatabase.synMapPathKey,
			                                        PathDatabase.synOptPathKey,
			                                        PathDatabase.placeAndRoutePathKey,
			                                        PathDatabase.synGenDelayKey,
			                                        PathDatabase.synMapDelayKey,
			                                        PathDatabase.synOptDelayKey,
			                                        PathDatabase.placeAndRouteDelayKey])
		else:
			expectedColumnList = [PathDatabase.cktNameKey,
			                      PathDatabase.startpointKey,
			                      PathDatabase.endpointKey,
			                      PathDatabase.targetCycleTimeKey,
			                      PathDatabase.synGenPathKey,
			                      PathDatabase.synMapPathKey,
			                      PathDatabase.synOptPathKey,
			                      PathDatabase.placeAndRoutePathKey,
			                      PathDatabase.synGenDelayKey,
			                      PathDatabase.synMapDelayKey,
			                      PathDatabase.synOptDelayKey,
			                      PathDatabase.placeAndRouteDelayKey]
			expectedColumnList = sorted(expectedColumnList)
			columnList = sorted(list(database.columns))
			if expectedColumnList != columnList:
				raise ValueError("Input dataframe has different column list")
			self.__database = database

	## Destructor
	#
	# \param self Instance of PathDatabase class.
	def __del__(self):
		# Delete dataframe
		del self.__database
		# Garbage collector
		gc.collect()

	## Access database
	#
	# \param self Instance of PathDatabase class.
	# \return Pandas Dataframe
	@property
	def database(self):
		return self.__database

	## Returns the number of rows in the database
	#
	# \param self Instance of PathDatabase class.
	# \return Integer
	@property
	def len(self):
		return int(self.database.shape[0])

	## Returns a string of the database to be printed
	#
	# \param self Instance of PathDatabase class.
	# \return Tabulated database to be printed
	def tabulate(self):
		return tabulate(self.database, headers='keys', tablefmt='psql')

	## Returns a random sample of the database
	#
	# \param self Instance of PathDatabase class.
	# \param numSamples Optional integer to define the number of samples to be collected. Default is all (0)
	# \return Dataframe
	def sample(self, numSamples=0):
		if not isinstance(numSamples, int):
			raise TypeError("numSamples must be a positive integer")
		elif numSamples < 0:
			raise ValueError("numSamples must be a positive integer")
		if numSamples == 0:
			numSamples = self.len
		return self.database.sample(numSamples)

	## Removes rows without a certain path
	#
	# \param self Instance of PathDatabase class.
	# \param pathKey Optional String defining the key to use for checking paths. Default is all
	# \return Dataframe
	def clean(self, pathKey=""):
		# Tests input
		if not isinstance(pathKey, str):
			raise TypeError("pathKey must be string")
		# Default is all types of path
		if pathKey == "":
			droppedRows = 0
			droppedRows += self.clean(pathKey=PathDatabase.synGenPathKey)
			droppedRows += self.clean(pathKey=PathDatabase.synMapPathKey)
			droppedRows += self.clean(pathKey=PathDatabase.synOptPathKey)
			droppedRows += self.clean(pathKey=PathDatabase.placeAndRoutePathKey)
			return droppedRows
		# Iterates through rows
		rowsToDrop = []
		for databaseDFIdx, databaseDFRow in self.database.iterrows():
			# Paths must have at least one cell
			if len(databaseDFRow[pathKey]) < 1:
				rowsToDrop.append(databaseDFIdx)
		# Removes rows and resets index
		if len(rowsToDrop) > 0:
			self.database.drop(self.database.index[rowsToDrop], inplace=True)
			self.database.reset_index(inplace=True)
		# Returns number of removed rows
		return len(rowsToDrop)

	## Gets information of a cell
	#
	# Expects cellDataList = [Rise/Fall, CellName, Fanout, Load, PropDelay, TranDelay]
	# Private method.
	#
	# \param self Instance of PathDatabase class.
	# \param cellDataList List of cell data
	# \param tranIn Float with input transition for current cell
	# \param cellNameRmRegexpList Optional List of Strings defining regexps used to clean cell names.
	# \param cellDrivingStregthRegexp Optional String defining a regexp used to collect the driving strength of cells. If empty (default), no driving strength is collected.
	# \return Tuple with (cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay)
	def __getCellInfo(self, cellDataList, tranIn, cellNameRmRegexpList=[], cellDrivingStregthRegexp = ""):
		# Initialize return values
		cellName = None
		cellDrive = None
		direction = None
		load = None
		fanout = None
		tranOut = None
		delay = None
		# Ignore gates w/ 0 delay (endpoints)
		if not(int(float(cellDataList[4])) == 0 or str(cellDataList[4]) == "-" or cellDataList[2] == "" or cellDataList[1] == ""):
			# Rise/Fall
			if cellDataList[0] == "F" or cellDataList[0] == "v":
				direction = -1
			else:
				direction = 1
			# Get cell name and clean
			cellName = cellDataList[1]
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
					cellDrive = re.sub('f', '', cellDrive)
					cellDrive = float(re.sub('p', '.', cellDrive))
				# If regexp didnt capture driving strength
				else:
					raise RuntimeError("ERROR! No match for cell %s with regexp %s" % (cellName, cellDrivingStregthRegexp))
			# Fanout
			fanout = int(cellDataList[2])
			# Load
			load = float(cellDataList[3])
			# delay
			delay = float(cellDataList[4])
			# Output transition
			tranOut = float(cellDataList[5])
			# Ensure types
			cellName = str(cellName)
			cellDrive = float(cellDrive)
			tranIn = float(tranIn)
		return cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay

	## Adds path information to dataframe
	#
	# If path does not exist yet, a new row is created. Private method.
	#
	# \param self Instance of PathDatabase class.
	# \param cktName String with the name of the circuit
	# \param targetCT Float with the target cycle time of paths in this circuit
	# \param pathType String with type of path, defined as those available in pathTypeList
	# \param startpoint String with the name of the startpoint
	# \param endpoint String with the name of the endpoint
	# \param path List with path to be added
	# \param pathDelay Float with delay of path to be added
	def __addToDatabase(self, cktName, targetCT, pathType, startpoint, endpoint, path, pathDelay):
		# If not in dataframe add it
		if not ((self.__database[PathDatabase.cktNameKey] == cktName) &
		        (self.__database[PathDatabase.targetCycleTimeKey] == targetCT) &
		        (self.__database[PathDatabase.startpointKey] == startpoint) &
		        (self.__database[PathDatabase.endpointKey] == endpoint)).any():
			dbIdx = self.__database.index
			if (len(dbIdx) == 0):
				dbIdx = 0
			else:
				dbIdx = max(self.__database.index) + 1
			self.__database.loc[dbIdx] = [cktName, startpoint, endpoint, targetCT, [], [], [], [], -1, -1, -1, -1]
		# Deal with different path types
		if pathType == PathDatabase.synGenPathTypeLabel:
			pathDelayLabel = PathDatabase.synGenDelayKey
			pathLabel = PathDatabase.synGenPathKey
		elif pathType == PathDatabase.synMapPathTypeLabel:
			pathDelayLabel = PathDatabase.synMapDelayKey
			pathLabel = PathDatabase.synMapPathKey
		elif pathType == PathDatabase.synOptPathTypeLabel:
			pathDelayLabel = PathDatabase.synOptDelayKey
			pathLabel = PathDatabase.synOptPathKey
		elif pathType == PathDatabase.placeAndRoutePathTypeLabel:
			pathDelayLabel = PathDatabase.placeAndRouteDelayKey
			pathLabel = PathDatabase.placeAndRoutePathKey
		else:
			raise RuntimeError("Unexpected error in __addToDatabase reading path type")
		# Check if path was already added in the dataframe previously
		dbIdxMatchList = self.__database.index[(self.__database[PathDatabase.cktNameKey] == cktName) &
		                                       (self.__database[PathDatabase.targetCycleTimeKey] == targetCT) &
		                                       (self.__database[PathDatabase.startpointKey] == startpoint) &
		                                       (self.__database[PathDatabase.endpointKey] == endpoint) &
		                                       (self.__database[pathDelayLabel] == -1)].tolist()
		# If already in dataframe, error
		if len(dbIdxMatchList) < 1:
			print(self.__database)
			raise RuntimeError("Path of type %s of circuit %s with target cycle time %f and startpoint/endpoint %s/%s was already added to the dataframe. Paths must be unique." % (pathType, cktName, targetCT, startpoint, endpoint))
		# Unexpected error
		elif len(dbIdxMatchList) > 1:
			raise RuntimeError("Unexpected error in __addToDatabase adding path to dataframe")
		# Otherwise, add data
		else:
			self.__database.at[dbIdxMatchList[0], pathLabel] = path
			self.__database.at[dbIdxMatchList[0], pathDelayLabel] = pathDelay

	## Reads a CSV file with path data and add to database.
	#
	# Expects the following format:
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
	#
	# \param self Instance of PathDatabase class.
	# \param csvPath String with path to CSV file to be read
	# \param cktName String with the name of the circuit
	# \param targetCT Float with the target cycle time of paths in this circuit
	# \param pathType String with type of path, defined as those available in pathTypeList
	# \param pathMinSize Optional Integer with minimum size of paths to be added. Default is 1
	# \param pathMaxSize Optional Integer with maximum size of paths to be added. Default is -1 (infinity)
	# \param cellDrivingStregthRegexp Optional String defining a regexp used to collect the driving strength of cells. If empty (default), no driving strength is collected.
	# \param startpointRmRegexpList Optional List of Strings defining regexps used to clean startpoint names.
	# \param endpointRmRegexpList Optional List of Strings defining regexps used to clean endpoint names.
	# \param cellNameRmRegexpList Optional List of Strings defining regexps used to clean cell names.
	def readCktFile(self, csvPath, cktName, targetCT,
	                pathType, pathMinSize=1, pathMaxSize=-1,
	                cellDrivingStregthRegexp="",
	                startpointRmRegexpList=[],
	                endpointRmRegexpList=[],
	                cellNameRmRegexpList=[]):
		# Validate inputs
		if not isinstance(csvPath, str):
			raise TypeError("csvPath must be a string")
		if not isinstance(cktName, str):
			raise TypeError("cktName must be a string")
		if not (isinstance(targetCT, float) or isinstance(targetCT, int)):
			raise TypeError("targetCT must be a float")
		if not isinstance(pathType, str):
			raise TypeError("pathType must be a string with one of the following options: %s" % self.pathTypeList)
		if not isinstance(pathMinSize, int):
			raise TypeError("pathMinSize must be an integer")
		if not isinstance(pathMaxSize, int):
			raise TypeError("pathMaxSize must be an integer")
		if not isinstance(cellDrivingStregthRegexp, str):
			raise TypeError("cellDrivingStregthRegexp must be a string")
		if not isinstance(startpointRmRegexpList, list):
			raise TypeError("startpointRmRegexpList must be a list of strings")
		for startpointRmRegexp in startpointRmRegexpList:
			if not isinstance(startpointRmRegexp, str):
				raise TypeError("startpointRmRegexpList must be a list of strings")
		if not isinstance(endpointRmRegexpList, list):
			raise TypeError("endpointRmRegexpList must be a list of strings")
		for endpointRmRegexp in endpointRmRegexpList:
			if not isinstance(endpointRmRegexp, str):
				raise TypeError("endpointRmRegexpList must be a list of strings")
		if not isinstance(cellNameRmRegexpList, list):
			raise TypeError("cellNameRmRegexpList must be a list of strings")
		for cellNameRmRegexp in cellNameRmRegexpList:
			if not isinstance(cellNameRmRegexp, str):
				raise TypeError("cellNameRmRegexpList must be a list of strings")
		# Read CSV file
		lineCount = 0
		with open(csvPath, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			# Initialize control variable that holds the label of a path
			pathDelay = None
			path = []
			startpoint = None
			endpoint = None
			for row in reader:
				if lineCount % 10000 == 0:
					print("Reading line %d of %s (%f)" % (lineCount, cktName, targetCT))
				lineCount = lineCount + 1
				# If new path found
				if re.match("^Path.*", row[0]):
					# If not first path to be found, add info
					if pathDelay is not None:
						# Filter by min max path size
						if not (len(path) < pathMinSize) or (len(path) > pathMaxSize):
							self.__addToDatabase(cktName=cktName, targetCT=targetCT, pathType=pathType,
							                     startpoint=startpoint, endpoint=endpoint,
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
					tranIn = 0.0
				# If inside a path
				else:
					# This is probably an error
					if pathDelay is None:
						raise RuntimeError("Unexpected error! readCktFile found invalid path!!")
					# Otherwise add to path
					else:
						# Collect cell information
						cellName, cellDrive, direction, tranIn, load, fanout, tranOut, delay = self.__getCellInfo(cellDataList=row, tranIn=tranIn, cellNameRmRegexpList=cellNameRmRegexpList, cellDrivingStregthRegexp=cellDrivingStregthRegexp)
						if cellName is not None:
							path.append([cellName, cellDrive, direction, fanout, load, tranIn, delay, tranOut])
							# Prepare for next iteration
							tranIn = tranOut
		# If still one last path to add
		if pathDelay is not None:
			# Filter by min max path size
			if not (len(path) < pathMinSize) or (len(path) > pathMaxSize):
				self.__addToDatabase(cktName=cktName, targetCT=targetCT, pathType=pathType,
				                     startpoint=startpoint, endpoint=endpoint,
				                     path=path, pathDelay=pathDelay)

	## Plots a database
	#
	# \param  self Instance of DirFileObj class.
	def plot(self):
		self.plotDelay()
		self.plotPathLength()
		self.plotPathLengthVsCriticality()
		self.plotPathVsCT()

	## Plots path length vs CT
	#
	# \param  self Instance of DirFileObj class.
	def plotPathVsCT(self):
		# Initialize dictionaries
		synGenCTDict = {}
		synMapCTDict = {}
		synOptCTDict = {}
		placeAndRouteCTDict = {}
		# Iterates through rows and populates dictionaries for synGen
		for databaseDFIdx, databaseDFRow in self.__database.iterrows():
			# Get path sizes and add to dictionaries when needed
			synGenPathSize = len(databaseDFRow[self.synGenPathKey])
			synGenCT = databaseDFRow[self.targetCycleTimeKey]
			if not synGenCT in synGenCTDict.keys():
				synGenCTDict[synGenCT] = []
			synGenCTDict[synGenCT].append(synGenPathSize)
		# Iterates through rows and populates dictionaries for synMap
		for databaseDFIdx, databaseDFRow in self.__database.iterrows():
			# Get path sizes and add to dictionaries when needed
			synMapPathSize = len(databaseDFRow[self.synMapPathKey])
			synMapCT = databaseDFRow[self.targetCycleTimeKey]
			if not synMapCT in synMapCTDict.keys():
				synMapCTDict[synMapCT] = []
			synMapCTDict[synMapCT].append(synMapPathSize)
		# Iterates through rows and populates dictionaries for synOpt
		for databaseDFIdx, databaseDFRow in self.__database.iterrows():
			# Get path sizes and add to dictionaries when needed
			synOptPathSize = len(databaseDFRow[self.synOptPathKey])
			synOptCT = databaseDFRow[self.targetCycleTimeKey]
			if not synOptCT in synOptCTDict.keys():
				synOptCTDict[synOptCT] = []
			synOptCTDict[synOptCT].append(synOptPathSize)
		# Iterates through rows and populates dictionaries for placeAndRoute
		for databaseDFIdx, databaseDFRow in self.__database.iterrows():
			# Get path sizes and add to dictionaries when needed
			placeAndRoutePathSize = len(databaseDFRow[self.placeAndRoutePathKey])
			placeAndRouteCT = databaseDFRow[self.targetCycleTimeKey]
			if not placeAndRouteCT in placeAndRouteCTDict.keys():
				placeAndRouteCTDict[placeAndRouteCT] = []
			placeAndRouteCTDict[placeAndRouteCT].append(placeAndRoutePathSize)
		# Create plots for detailed analysis
		fig = make_subplots(rows=2, cols=2, subplot_titles=(self.targetCycleTimeKey,
		                                                    self.targetCycleTimeKey,
		                                                    self.targetCycleTimeKey,
		                                                    self.targetCycleTimeKey))
		for synGenCT in sorted(list(synGenCTDict.keys())):
			fig.add_trace(go.Box(y=synGenCTDict[synGenCT], boxpoints='all', name=synGenCT), row=1, col=1)
		for synMapCT in sorted(list(synMapCTDict.keys())):
			fig.add_trace(go.Box(y=synMapCTDict[synMapCT], boxpoints='all', name=synMapCT), row=1, col=2)
		for synOptCT in sorted(list(synOptCTDict.keys())):
			fig.add_trace(go.Box(y=synOptCTDict[synOptCT], boxpoints='all', name=synOptCT), row=2, col=1)
		for placeAndRouteCT in sorted(list(placeAndRouteCTDict.keys())):
			fig.add_trace(go.Box(y=placeAndRouteCTDict[placeAndRouteCT], boxpoints='all', name=placeAndRouteCT), row=2, col=2)
		fig.update_layout(title="Path vs CT", height=900, width=1800, showlegend=False)
		fig.show()

	## Plots path length vs the criticality of paths of a database
	#
	# \param  self Instance of DirFileObj class.
	def plotPathLengthVsCriticality(self):
		# Initialize dictionaries
		synGenPathDict = {}
		synMapPathDict = {}
		synOptPathDict = {}
		placeAndRoutePathDict = {}
		# Iterates through rows and populates dictionaries
		for databaseDFIdx, databaseDFRow in self.__database.iterrows():
			# Get criticality of path
			pathCriticality = databaseDFRow[self.placeAndRouteDelayKey]/databaseDFRow[self.targetCycleTimeKey]
			pathCriticality = pathCriticality*10
			pathCriticality = int(pathCriticality)/10
			# Create key in dictionaries if needed
			if not pathCriticality in synGenPathDict.keys():
				synGenPathDict[pathCriticality] = []
			if not pathCriticality in synMapPathDict.keys():
				synMapPathDict[pathCriticality] = []
			if not pathCriticality in synOptPathDict.keys():
				synOptPathDict[pathCriticality] = []
			if not pathCriticality in placeAndRoutePathDict.keys():
				placeAndRoutePathDict[pathCriticality] = []
			# Get path sizes
			synGenPathSize = len(databaseDFRow[self.synGenPathKey])
			synMapPathSize = len(databaseDFRow[self.synMapPathKey])
			synOptPathSize = len(databaseDFRow[self.synOptPathKey])
			placeAndRoutePathSize = len(databaseDFRow[self.placeAndRoutePathKey])
			# Add path sizes to dictionary
			synGenPathDict[pathCriticality].append(synGenPathSize)
			synMapPathDict[pathCriticality].append(synMapPathSize)
			synOptPathDict[pathCriticality].append(synOptPathSize)
			placeAndRoutePathDict[pathCriticality].append(placeAndRoutePathSize)
		# Create plots for detailed analysis
		fig = make_subplots(rows=2, cols=2, subplot_titles=("synGen",
		                                                     "synMap",
		                                                     "synOpt",
		                                                     "placeAndRoute"))
		for synGenPathCriticality in sorted(list(synGenPathDict.keys())):
			fig.add_trace(go.Box(y=synGenPathDict[synGenPathCriticality], boxpoints='all', name=synGenPathCriticality), row=1, col=1)
		for synMapPathCriticality in sorted(list(synMapPathDict.keys())):
			fig.add_trace(go.Box(y=synMapPathDict[synMapPathCriticality], boxpoints='all', name=synMapPathCriticality), row=1, col=2)
		for synOptPathCriticality in sorted(list(synOptPathDict.keys())):
			fig.add_trace(go.Box(y=synOptPathDict[synOptPathCriticality], boxpoints='all', name=synOptPathCriticality), row=2, col=1)
		for placeAndRoutePathCriticality in sorted(list(placeAndRoutePathDict.keys())):
			fig.add_trace(go.Box(y=placeAndRoutePathDict[placeAndRoutePathCriticality], boxpoints='all', name=placeAndRoutePathCriticality), row=2, col=2)
		fig.update_layout(title="Path Length vs Criticality", height=900, width=1800, showlegend=False)
		fig.show()

	## Plots the path length distributions of a database
	#
	# \param  self Instance of DirFileObj class.
	def plotPathLength(self):
		# Get list of path length for synGen
		synGenPathLengthList = []
		synGenPathList = self.__database[self.synGenPathKey].tolist()
		for synGenPath in synGenPathList:
			synGenPathLengthList.append(len(synGenPath))
		# Get list of path length for synMap
		synMapPathLengthList = []
		synMapPathList = self.__database[self.synMapPathKey].tolist()
		for synMapPath in synMapPathList:
			synMapPathLengthList.append(len(synMapPath))
		# Get list of path length for synOpt
		synOptPathLengthList = []
		synOptPathList = self.__database[self.synOptPathKey].tolist()
		for synOptPath in synOptPathList:
			synOptPathLengthList.append(len(synOptPath))
		# Get list of path length for pnr
		placeAndRoutePathLengthList = []
		placeAndRoutePathList = self.__database[self.placeAndRoutePathKey].tolist()
		for placeAndRoutePath in placeAndRoutePathList:
			placeAndRoutePathLengthList.append(len(placeAndRoutePath))
		# Create plots for detailed analysis
		fig = make_subplots(rows=2, cols=2, subplot_titles=(self.synGenPathKey,
		                                                    self.synMapPathKey,
		                                                    self.synOptPathKey,
		                                                    self.placeAndRoutePathKey))
		fig.add_trace(go.Histogram(x=synGenPathLengthList), row=1, col=1)
		fig.add_trace(go.Histogram(x=synMapPathLengthList), row=1, col=2)
		fig.add_trace(go.Histogram(x=synOptPathLengthList), row=2, col=1)
		fig.add_trace(go.Histogram(x=placeAndRoutePathLengthList), row=2, col=2)
		fig.update_layout(title="Path Length Distribution", height=900, width=1800, showlegend=False)
		fig.show()

	## Plots the delay distributions of a database
	#
	# \param  self Instance of DirFileObj class.
	def plotDelay(self):
		synGenDelayList = self.__database[self.synGenDelayKey].tolist()
		synMapDelayList = self.__database[self.synMapDelayKey].tolist()
		synOptDelayList = self.__database[self.synOptDelayKey].tolist()
		placeAndRouteDelayList = self.__database[self.placeAndRouteDelayKey].tolist()
		# Create plots for detailed analysis
		fig = make_subplots(rows=2, cols=2, subplot_titles=(self.synGenDelayKey,
		                                                    self.synMapDelayKey,
		                                                    self.synOptDelayKey,
		                                                    self.placeAndRouteDelayKey))
		fig.add_trace(go.Histogram(x=synGenDelayList), row=1, col=1)
		fig.add_trace(go.Histogram(x=synMapDelayList), row=1, col=2)
		fig.add_trace(go.Histogram(x=synOptDelayList), row=2, col=1)
		fig.add_trace(go.Histogram(x=placeAndRouteDelayList), row=2, col=2)
		fig.update_layout(title="Delay Distribution", height=900, width=1800, showlegend=False)
		fig.show()