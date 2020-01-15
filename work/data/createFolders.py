################################################################################
# Libraries
################################################################################
import os
import shutil
import sys
pytomationHome = os.environ['PYTOMATION_HOME']
sys.path.append(os.path.realpath(pytomationHome+"/src/fileTypes"))
from DirFileObj import DirFileObj
################################################################################
# Configuration
################################################################################
synthFileName       = "synthesis.tcl"
placeHolderCktName  = "_CKT_NAME_"
placeHolderCktComb  = "_CKT_COMB_"
placeHolderTargetCT = "_TARGET_CT_"
stdFlowDirName      = "stdFlow"
hdlDirName          = "hdl"
cktDict = {
	"adder" : {
		"targetCT" : 100,
		"comb" : 1
	},
	"mem_ctrl" : {
		"targetCT" : 100,
		"comb" : 0
	}
}
################################################################################
# Remove folders
################################################################################
if os.path.exists(stdFlowDirName):
	shutil.rmtree(stdFlowDirName)
################################################################################
# Create folders
################################################################################
hdlPath = os.path.realpath(hdlDirName)
templateRootDir = DirFileObj(path=os.path.realpath("./template"))
print("Creating folders for std flow at %s" % stdFlowDirName)
stdFlowTemplateDir = templateRootDir.getDir(stdFlowDirName)
stdFlowDir = DirFileObj(path=os.path.realpath(stdFlowDirName))
# Run for all circuits
for ckt in cktDict.keys():
	targetCT = cktDict[ckt]["targetCT"]
	comb = cktDict[ckt]["comb"]
	print("  Circuit is %s" % ckt)
	print("    Target CT = %d" % targetCT)
	print("    Comb      = %d" % comb)
	folderName = ckt+"_"+str(targetCT)
	stdFlowCktDir = stdFlowTemplateDir.copy(name=folderName, father=stdFlowDir)
	synthFile = stdFlowCktDir.getFile(synthFileName)
	synthFile.strSub(placeHolderCktName, ckt)
	synthFile.strSub(placeHolderCktComb, str(comb))
	synthFile.strSub(placeHolderTargetCT, str(targetCT))
# Write folders
stdFlowDir.write()
