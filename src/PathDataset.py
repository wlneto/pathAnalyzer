## \file PathDataset.py
#  \brief Class ..
#
# Aaa
#
# Revision | Author            | Date     | Comment
#:---------|:------------------|:---------|:----------------
# 1.0      | Matheus T. M.     | 12/31/19 | Initial version
# 1.1      | Matheus T. M.     | 01/17/20 | Enhancing add function, adding split and plot functions
# 1.2      | Matheus T. M.     | 01/18/20 | Updating add function to use new algorithm for creating labels
# 1.3      | Matheus T. M.     | 01/26/20 | Updating methods to support mapped gates data and upgrading gate dictionary
#

import gc
# import random
import pandas as pd
from tabulate import tabulate
from PathDatabase import PathDatabase
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class PathDataset(object):
	# Keys
	cktNameKey       = "cktName"
	dataTypeKey      = "dataType"
	startpointKey    = "startpoint"
	endpointKey      = "endpoint"
	databaseIdxKey   = "databaseIdx"
	featureTensorKey = "featureTensor"
	labelKey         = "label"
	# Labels
	trainDataLabel      = "train"
	validationDataLabel = "validation"
	testDataLabel       = "test"
	unassignedDataLabel = "unassigned"

	## Constructor
	#
	# \param self Instance of PathDataset class.
	# \param pathSize Integer defining the size of paths in this dataset
	def __init__(self, pathSize):
		# Validate input
		if not isinstance(pathSize, int):
			raise TypeError("pathSize must be an integer greater than 0")
		if pathSize < 1:
			raise ValueError("pathSize must be an integer greater than 0")
		super(PathDataset, self).__init__()

		self.__dataset = pd.DataFrame(columns=[PathDataset.cktNameKey,
		                                       PathDataset.databaseIdxKey,
		                                       PathDataset.startpointKey,
		                                       PathDataset.endpointKey,
		                                       PathDataset.dataTypeKey,
		                                       PathDataset.featureTensorKey,
		                                       PathDataset.labelKey])

		self.__pathSize = pathSize

	## Destructor
	#
	# \param self Instance of PathDataset class.
	def __del__(self):
		# Delete dataframe
		del self.__dataset
		# Garbage collector
		gc.collect()

	## Access cellMap
	# Collected average delays using:
	# grep INVx *.csv | sed 's#.*,##g'  | awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'
	#
	# \param self Instance of PathDataset class.
	# \return Dictionary mapping cells
	@property
	def cellMap(self):
		return {"not" : 27.0927, 
		        "nand2" : 28.5269,
		        "nor2" : 35.9054,
		        "and2" : 26.7959,
		        "or2" : 34.5984,
		        "complex2" : 22.106,
		        "d_flop" : 23.2254,
		        "INV" : 27.0927,
		        "AND2" : 26.7959,
		        "AND3" : 22.2191,
		        "AND4" : 26.1565,
		        "AND5" : 27.3621,
		        "A2O1A1I" : 24.4815,
		        "A2O1A1O1I" : 28.0788,
		        "AO21" : 14.6993,
		        "AO22" : 19.0622,
		        "AO221" : 18.6065,
		        "AO32" : 17.4794,
		        "AO33" : 19.6495,
		        "AO331" : 17.3897,
		        "AO332" : 33.7483,
		        "AOI21" : 19.9716,
		        "AOI211" : 25.4058,
		        "AOI22" : 24.3963,
		        "AOI221" : 27.1355,
		        "AOI222" : 32.4737,
		        "AOI31" : 23.7634,
		        "AOI311" : 25.1277,
		        "AOI32" : 29.0516,
		        "AOI321" : 31.0311,
		        "AOI322" : 33.2888,
		        "AOI33" : 30.5441,
		        "AOI331" : 37.0556,
		        "AOI332" : 45.632,
		        "BUF" : 26.2378,
		        "DFFHQ" : 23.2254,
		        "DFFHQN" : 33.5044,
		        "HA" : 27.7183,
		        "FA" : 55.1946,
		        "HB1" : 21.8976,
		        "NAND2" : 28.5269,
		        "NAND3" : 20.4143,
		        "NAND4" : 23.5301,
		        "NAND5" : 26.6561,
		        "NOR2" : 35.9054,
		        "NOR3" : 25.6108,
		        "NOR4" : 30.6857,
		        "NOR5" : 42.7612,
		        "O2A1O1I" : 24.7271,
		        "OA21" : 17.2617,
		        "OA211" : 24.3438,
		        "OA22" : 18.1011,
		        "OA33" : 20.0235,
		        "OA331" : 26.14,
		        "OA332" : 16.0517,
		        "OAI21" : 18.6489,
		        "OAI211" : 22.9415,
		        "OAI22" : 26.6829,
		        "OAI221" : 25.5124,
		        "OAI222" : 26.7465,
		        "OAI31" : 22.5325,
		        "OAI311" : 23.5224,
		        "OAI32" : 28.6801,
		        "OAI321" : 29.93,
		        "OAI322" : 35.8976,
		        "OAI331" : 34.9563,
		        "OAI332" : 35.1733,
		        "OR2" : 34.5984,
		        "OR3" : 24.9962,
		        "OR4" : 29.4929,
		        "OR5" : 36.6566,
		        "SDFH" : 15.9394,
		        "XNOR2" : 27.8183,
		        "XOR2" : 30.0836}

	## Access pathSize
	#
	# \param self Instance of PathDataset class.
	# \return Integer
	@property
	def pathSize(self):
		return self.__pathSize

	## Access dataset
	#
	# \param self Instance of PathDataset class.
	# \return Pandas Dataframe
	@property
	def dataset(self):
		return self.__dataset

	## Returns the number of rows in the dataset
	#
	# \param self Instance of PathDataset class.
	# \return Integer
	@property
	def len(self):
		return int(self.dataset.shape[0])

	## Returns a string of the database to be printed
	#
	# \param self Instance of PathDataset class.
	# \return Tabulated database to be printed
	def tabulate(self):
		return tabulate(self.dataset, headers='keys', tablefmt='psql')

	## Adds data to the dataset
	#
	# Gets a sample of numSample data points from pathDB. Then analize samples
	# to create tensors modeling paths as:
	# [cell0, cell1, ..., celln]
	# Where a cell is modeled as:
	# [targetCT, cellName, cellDirection, cellFanout, cellLoad]
	# Next collect labels. These are binary values generating according to how
	# critical a path is. Paths that have their delay/targetCT bigget than the
	# threshold defined by critPathTh will have a label=1, others will have a
	# label=0.
	#
	# \param self Instance of PathDataset class.
	# \param pathDB PathDatabase with the database from which data is to be collected
	# \param numSamples Optional integer to define the number of samples to be collected. Default is all (0)
	# \param critPathTh Optional float to define the threshold used to define critical paths. Default is 0.8
	# \param pathKey Optional string defining the key to use when collecting paths
	# \param delayKey Optional string defining the key to use when collecting path delays
	# \param targetCTDivisionFactor Optional float defining division factor to use on target CTs
	# \param fanoutDivisionFactor Optional float defining division factor to use on fanouts
	def add(self, pathDB, numSamples=0, critPathTh=0.8, pathKey=PathDatabase.synGenPathKey, delayKey=PathDatabase.placeAndRouteDelayKey, targetCTDivisionFactor=1000.0, fanoutDivisionFactor=100.0):
		# Validate inputs
		if not isinstance(pathDB, PathDatabase):
			raise TypeError("pathDB must be a PathDatabase")
		if not isinstance(numSamples, int):
			raise TypeError("numSamples must be a positive integer")
		elif numSamples < 0:
			raise ValueError("numSamples must be a positive integer")
		if not isinstance(pathKey, str):
			raise TypeError("pathKey must be string")
		if not isinstance(delayKey, str):
			raise TypeError("delayKey must be string")
		if not isinstance(targetCTDivisionFactor, float):
			raise TypeError("targetCTDivisionFactor must be a float")
		if not isinstance(fanoutDivisionFactor, float):
			raise TypeError("fanoutDivisionFactor must be a float")
		# Default to all
		if numSamples < 0:
			numSamples = len(pathDB.database.index.to_list())
		# Get maximum cell cost
		maxCellCost = 0.0
		for cellName in self.cellMap.keys():
			if self.cellMap[cellName] > maxCellCost:
				maxCellCost = self.cellMap[cellName]
		# print("Max cell cost is %f" % maxCellCost)
		# Collect sample of database (only paths with more than 0 cells)
		sampleDatabaseDF = pathDB.sample(numSamples=numSamples,)
		# Iterate through samples and add to dataset
		for sampleDatabaseDFIdx, sampleDatabaseDFRow in sampleDatabaseDF.iterrows():
			# Make sure input data is valid
			if not isinstance(sampleDatabaseDFRow[PathDatabase.cktNameKey], str):
				raise TypeError("Wrong format for ckt name in database. Must be string.")
			if not isinstance(sampleDatabaseDFRow[PathDatabase.startpointKey], str):
				raise TypeError("Wrong format for startpoint in database. Must be string.")
			if not isinstance(sampleDatabaseDFRow[PathDatabase.endpointKey], str):
				raise TypeError("Wrong format for endpoint in database. Must be string.")
			if not isinstance(sampleDatabaseDFRow[pathKey], list):
				raise TypeError("Wrong format for path in database. Must be list.")
			# Get target CT and delay
			targetCT = float(sampleDatabaseDFRow[PathDatabase.targetCycleTimeKey])
			if targetCT < 0.0:
				raise ValueError("Path CT must be grater than 0. Read %f." % targetCT)
			pathDelay = float(sampleDatabaseDFRow[delayKey])
			if pathDelay < 0.0:
				raise ValueError("Path delay must be grater than 0. Read %f." % pathDelay)
			# Get cktName, start and end point
			cktName = sampleDatabaseDFRow[PathDatabase.cktNameKey]
			startpoint = sampleDatabaseDFRow[PathDatabase.startpointKey]
			endpoint = sampleDatabaseDFRow[PathDatabase.endpointKey]
			# Get path
			path = sampleDatabaseDFRow[pathKey]
			# Collect label
			if float(pathDelay)/float(targetCT) > critPathTh:
				label = 1
			else:
				label = 0
			# Create tensor
			featureTensor = []
			# Adjust CT before adding to tensor
			targetCT = targetCT / targetCTDivisionFactor
			# Iterate through path to format data and add to tensor
			for pathCell in path:
				pathCellName = pathCell[0]
				# pathCellDrive = pathCell[1]
				pathCellDirection = pathCell[2]
				pathCellFanout = pathCell[3]
				pathCellLoad = pathCell[4]
				# pathCellTranIn = pathCell[5]
				pathCellName = self.cellMap[pathCellName]
				pathCellName = float(pathCellName)/float(maxCellCost)
				pathCellFanout = pathCellFanout / fanoutDivisionFactor
				# featureTensor.append([targetCT, pathCellName, pathCellDrive, pathCellDirection, pathCellFanout, pathCellLoad])
				featureTensor.append([targetCT, pathCellName, pathCellDirection, pathCellFanout, pathCellLoad])
				# Stop when reached pathSize
				if len(featureTensor) == self.pathSize:
					break
				# This cant happen
				elif len(featureTensor) > self.pathSize:
					raise RuntimeError("Unexpected error adding paths. Read tensor with size %d and max size is %d" % (len(featureTensor), self.pathSize))
			# Add padding to tensor
			for padIdx in range(len(featureTensor),self.pathSize):
				featureTensor.append(len(featureTensor[0])*[0])
			# Set index
			dbIdx = self.dataset.index
			if (len(dbIdx) == 0):
				dbIdx = 0
			else:
				dbIdx = max(self.dataset.index) + 1
			# Add new row to dataset
			self.dataset.loc[dbIdx] = [cktName,
			                           sampleDatabaseDFIdx,
			                           startpoint,
			                           endpoint,
			                           PathDataset.unassignedDataLabel,
			                           featureTensor,
			                           label]

	## Split dataset in training, validation and testing
	#
	# \param self Instance of PathDataset class.
	# \param trainPct Optional float defining the percentage of features to be used for training
	# \param valPct Optional float defining the percentage of features to be used for validation
	# \param testPct Optional float defining the percentage of features to be used for test
	def split(self, trainPct=0.5, valPct=0.3, testPct=0.2):
		# Validate inputs
		if not isinstance(trainPct, float):
			raise TypeError("trainPct must be a float")
		if not isinstance(valPct, float):
			raise TypeError("valPct must be a float")
		if not isinstance(testPct, float):
			raise TypeError("testPct must be a float")
		if trainPct <= 0.0:
			raise ValueError("trainPct must be greater than 0")
		if valPct <= 0.0:
			raise ValueError("valPct must be greater than 0")
		if testPct < 0.0:
			raise ValueError("testPct must be greater or equal to 0")
		if trainPct+valPct+testPct > 1.0:
			raise ValueError("Summation of train, val and test percentages must be lesser or equal to one")
		# Define split points
		trainSplit = int(trainPct*self.len)
		valSplit = int(valPct*self.len)+trainSplit
		testSplit = int(testPct*self.len)+valSplit
		# Iterate through dataset to assign
		for datasetIdx, datasetRow in self.dataset.iterrows():
			# Set data type
			if datasetIdx < trainSplit:
				dataType=PathDataset.trainDataLabel
			elif datasetIdx < valSplit:
				dataType=PathDataset.validationDataLabel
			elif datasetIdx < testSplit:
				dataType=PathDataset.testDataLabel
			else:
				dataType=PathDataset.unassignedDataLabel
			self.dataset.at[datasetIdx, PathDataset.dataTypeKey] = dataType

	## Plots the relation between tensor values and labels
	#
	# \param self Instance of PathDataset class.
	def plotTensorToFeature(self):
		# Initialize control variables
		# maxCT = 0
		# maxCell = 0
		maxFO = 0
		maxLoad = 0
		# Intialize data structures to hold info for analysis
		labelList = []
		totalFOList = []
		totalLoadList = []
		textList = []
		# Iterate through dataset to assign
		for datasetIdx, datasetRow in self.dataset.iterrows():
			labelList.append(float(datasetRow[PathDataset.labelKey]))
			startpoint = datasetRow[PathDataset.startpointKey]
			endpoint = datasetRow[PathDataset.endpointKey]
			textList.append(startpoint+"->"+endpoint)
			featureTensor = datasetRow[PathDataset.featureTensorKey]
			totalFO = 0
			totalLoad = 0
			for cell in featureTensor:
				# targetCT = cell[0]
				# cellName = cell[1]
				cellFO = float(cell[3])
				if cellFO > maxFO:
					maxFO = cellFO
				totalFO += cellFO
				cellLoad = float(cell[4])
				if cellLoad > maxLoad:
					maxLoad = cellLoad
				totalLoad += cellLoad
			totalFOList.append(totalFO)
			totalLoadList.append(totalLoad)
		fig = make_subplots(rows=1, cols=4, subplot_titles=("FO vs Label", "Load vs Label"))
		fig.add_trace(go.Scatter(x=totalFOList,y=labelList,text=textList,mode="markers",name="FO"), row=1, col=1)
		fig.add_trace(go.Scatter(x=totalLoadList,y=labelList,text=textList,mode="markers",name="Load"), row=1, col=2)
		fig.show()
