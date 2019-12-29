################################################################################
# Libraries
################################################################################
import pickle
import os
import plotly.graph_objects as go
################################################################################
# Config
################################################################################
inputFileName = "neuralNetwork0.pkl"
################################################################################
# Load data
################################################################################
if os.path.exists(inputFileName):
	with open(inputFileName, 'rb') as f:
		inDict = pickle.load(f)
	f.close()
else:
	raise RuntimeError("ERROR! Couldn't find file %s" % (inputFileName))
################################################################################
# Plots
################################################################################
lossListY = inDict["lossList"]
lossListX = list(range(len(lossListY)))
valLossListY = inDict["valLossList"]
valLossListX = list(range(len(valLossListY)))
fig0 = go.Figure(data=[go.Scatter(x=lossListX,y=lossListY,name="Training Loss"),
                       go.Scatter(x=valLossListX,y=valLossListY,name="Validation Loss")])
fig0.show()
testLabelList = inDict["testLabelList"]
testPredictList = inDict["testPredictList"]
testErrorList = inDict["testErrorList"]
fig1 = go.Figure(data=[go.Scatter(x=testLabelList,y=testPredictList,text=testErrorList,mode="markers",name="Prediction"),go.Scatter(x=testLabelList,y=testLabelList,name="Ideal"),go.Scatter(x=testLabelList,y=1.1*testLabelList),go.Scatter(x=testLabelList,y=0.9*testLabelList)])
fig1.update_layout(title="Max Error = %f" % max(testErrorList))
fig1.show()
