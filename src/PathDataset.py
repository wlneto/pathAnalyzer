## \file PathDataset.py
#  \brief Class ..
#
# Aaa
#
# Revision | Author            | Date     | Comment
#:---------|:------------------|:---------|:----------------
# 1.0      | Matheus T. M.     | 12/31/19 | Initial version
#

import gc
# import random
import pandas as pd
from tabulate import tabulate
from PathDatabase import PathDatabase

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
	#
	# \param self Instance of PathDataset class.
	# \return Dictionary mapping cells
	@property
	def cellMap(self):
		return {"not" : 0, "nand2" : 1, "nor2" : 1, "and2" : 2, "or2" : 2, "complex2" : 3, "d_flop" : 4}

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
	# \param self Instance of PathDataset class.
	# \param pathDB PathDatabase with the database from which data is to be collected
	# \param numSamples Optional integer to define the number of samples to be collected. Default is all (0)
	# \param pathKey Optional string defining the key to use when collecting paths
	# \param delayKey Optional string defining the key to use when collecting path delays
	# \param targetCTDivisionFactor Optional float defining division factor to use on target CTs
	# \param fanoutDivisionFactor Optional float defining division factor to use on fanouts
	def add(self, pathDB, numSamples=0, pathKey=PathDatabase.synGenPathKey, delayKey=PathDatabase.placeAndRouteDelayKey, targetCTDivisionFactor=1000.0, fanoutDivisionFactor=100.0):
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
		# Collect sample of database
		sampleDatabaseDF = pathDB.sample(numSamples)
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
			label = float(pathDelay)/float(targetCT)
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
				pathCellName = float(pathCellName)/float(len(list(self.cellMap.keys())))
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
	def plotTensorRel(self):
		targetCTList = []
		pathCellNameList = []
		pathCellDirection, pathCellFanout, pathCellLoad
		# Iterate through dataset to assign
		for datasetIdx, datasetRow in self.dataset.iterrows():