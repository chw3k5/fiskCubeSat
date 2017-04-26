import getpass
import numpy
import os
from matplotlib import pyplot as plt

from pulse.pulseReadIn import saveProcessedData, readInSavedRowData
from pulse.pulseOperations import extractPulseInfo, removeOutliers, initializeTestPlots, appendToTestPlots
from peak.gaussFitter import gaussian
from peak.mariscotti import peakFinder
from quickPlots import quickHistograms, ls, quickPlotter


class pulseGroup():
    def __init__(self, listOfPulseDicts=[]):
        self.listOfPulseDicts = listOfPulseDicts


    def processPulses(self,
                      folderName,
                      fileNamePrefix='',
                      filenameSuffix='.txt',
                      columnNamesToIgnore=['time'],
                      skipRows=3,
                      delimiter='\t',
                      trimBeforeMin=True,
                      multiplesOfMedianStdForRejection=1000.0, # None or float, None means no rejection
                      conv_channels=1,
                      numOfExponents=2,
                      upperBoundAmp=float(1000),
                      showTestPlots_Pulses=False,
                      testModeReadIn=False,
                      verbose=True):

        self.listOfPulseDicts = extractPulseInfo(folderName=folderName,
                                                 fileNamePrefix=fileNamePrefix,
                                                 filenameSuffix=filenameSuffix,
                                                 columnNamesToIgnore=columnNamesToIgnore,
                                                 skipRows=skipRows,
                                                 delimiter=delimiter,
                                                 trimBeforeMin=trimBeforeMin,
                                                 multiplesOfMedianStdForRejection=multiplesOfMedianStdForRejection,
                                                 conv_channels=conv_channels,
                                                 numOfExponents=numOfExponents,
                                                 upperBoundAmp=upperBoundAmp,
                                                 showTestPlots_Pulses=showTestPlots_Pulses,
                                                 testModeReadIn=testModeReadIn)


    def getSavedPulses(self,
                       folderName,
                       pulseDataTypes,
                       fileNamePrefix='',
                       filenameSuffix='.csv'):
        listOfPulseDicts = self.listOfPulseDicts[:]
        for pulseDataType in pulseDataTypes:
            fileName = os.path.join(folderName, fileNamePrefix + pulseDataType + filenameSuffix)

            listOfPulseDicts = readInSavedRowData(fileName, pulseDataType, listOfPulseDicts)
        self.listOfPulseDicts = listOfPulseDicts


    def makeOutputDict(self, pulseDataTypesToExtract):
        self.outputDict = {}
        if 'uniqueID' not in pulseDataTypesToExtract:
            pulseDataTypesToExtract.append('uniqueID')
        for pulseDataType in pulseDataTypesToExtract:
            self.outputDict[pulseDataType] = []
        # do this operation for each pulse dictionary in this class
        for pulseDict in self.listOfPulseDicts:
            # extract the required data types for output
            removeFlag = False
            for pulseDataType in pulseDataTypesToExtract:
                # if a data type is None we flag to remove this pulse before it get in with the rest of the data
                if pulseDict[pulseDataType] is None:
                    removeFlag = True
            if not removeFlag:
                for pulseDataType in pulseDataTypesToExtract:
                    datum = pulseDict[pulseDataType]
                    try:
                        self.outputDict[pulseDataType].append(float(datum))
                    except ValueError:
                        self.outputDict[pulseDataType].append(datum)

        # Change the data from a lists to arrays
        for pulseDataType in self.outputDict.keys():
            self.outputDict[pulseDataType] = numpy.array(self.outputDict[pulseDataType])


    def saveOutputDict(self, outPutFileBase, saveDataType,
                       maxDataArraysPerFile=100, delimiter=',',
                       saveAsColumns=False, verbose=True):
        if 'uniqueID' in pulseDataTypesToSave:
            pulseDataTypesToSave.remove('uniqueID')
        for saveDataType in pulseDataTypesToSave:
            listOfHeaderNames = self.outputDict['uniqueID']
            listOfDataArrays = self.outputDict[saveDataType]
            fileBaseName = outPutFileBase + '_' + saveDataType
            saveProcessedData(listOfHeaderNames, listOfDataArrays, fileBaseName,
                              maxDataArraysPerFile=maxDataArraysPerFile, delimiter=delimiter,
                              saveAsColumns=saveAsColumns, verbose=verbose)


    def removeOutliers(self, parameter, multiplesOfMedianStdForRejection=5.0):
        self.makeOutputDict([parameter])
        oldArray, keepMask = removeOutliers(self.outputDict[parameter],
                                            multiplesOfMedianStdForRejection=multiplesOfMedianStdForRejection)
        newListOfPulsesDicts = []
        for (listIndex, keepFlag) in list(enumerate(keepMask)):
            if keepFlag:
                newListOfPulsesDicts.append(self.listOfPulseDicts[listIndex])
        self.listOfPulseDicts = newListOfPulsesDicts


    def findGroupPeaks(self):
        pass





# folderList = [
#     'CHC alpha_gamma traces']
folderList = ['CHC alpha traces',
              'CHC alpha traces thrsh 180',
              'CHC alpha_gamma traces',
              'CHC gamma traces']
numOfExponents = 2
# pulseDataForHistogram = ['integral', 'fittedCost']
# for index in range(numOfExponents):
#     pulseDataForHistogram.extend(['fittedAmp' + str(index + 1), 'fittedTau' + str(index + 1)]) # this turn into keys for a dictionary that extractPulseInfo Outputs
#
# pulseDataTypesToRemoveOutliers = [('fittedCost', float(5)), ('integral', float(20)),
#                                   ('fittedAmp1', float(20)), ('fittedTau1', float(20)),
#                                   ('fittedAmp2', float(20)), ('fittedTau2', float(20)),
#                                   ('fittedAmp3', float(20)), ('fittedTau3', float(20)),
#                                   ('fittedAmp4', float(20)), ('fittedTau4', float(20))]
pulseDataTypesToRemoveOutliers = [('integral', float(100)), ('fittedCost', float(4)),
                                  ('fittedAmp1', float(100)), ('fittedTau1', float(100)),
                                  ('fittedAmp2', float(100)), ('fittedTau2', float(100))]
pulseDataTypesToSave = ['integral', 'fittedCost', 'fittedAmp1', 'fittedTau1', 'fittedAmp2', 'fittedTau2']



showTestPlots_Pulses = False
showHistPlots = False
showPeakFinderPlot = False
saveHistPlots = True
histBins = 60

errFactorForPeakFinder = 1

testModeReadIn = False
verbose = True

if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
    parentFolder = '/Users/chw3k5/Desktop/new CHC traces'
else:
    parentFolder = ''


plotFolder = os.path.join(parentFolder, 'plots')
if not os.path.exists(plotFolder):
    os.mkdir(plotFolder)

outputFolder = os.path.join(parentFolder, 'output')
if not os.path.exists(outputFolder):
    os.mkdir(outputFolder)


def doExtractAndSavePulseInfo(parentFolder, folderList, outputFolder, pulseDataTypesToSave):
    groupDict = {}
    for singleFolder in folderList:
        folderName = os.path.join(parentFolder, singleFolder)
        groupDict[singleFolder] = pulseGroup()
        groupDict[singleFolder].processPulses(folderName=folderName,
                                              fileNamePrefix=singleFolder + '_',
                                              filenameSuffix='.txt',
                                              columnNamesToIgnore=['time'],
                                              skipRows=3,
                                              delimiter='\t',
                                              trimBeforeMin=True,
                                              multiplesOfMedianStdForRejection=1000.0, # None or float, None means no rejection
                                              conv_channels=1,
                                              numOfExponents=numOfExponents,
                                              upperBoundAmp=float(1000),
                                              showTestPlots_Pulses=showTestPlots_Pulses,
                                              testModeReadIn=testModeReadIn,
                                              verbose=verbose)

        outPutFileBase = os.path.join(outputFolder, singleFolder)
        if pulseDataTypesToSave != []:
            groupDict[singleFolder].makeOutputDict(pulseDataTypesToSave)
            for saveDataType in pulseDataTypesToSave:
                groupDict[singleFolder].saveOutputDict(outPutFileBase=outPutFileBase, saveDataType=saveDataType,
                                                       maxDataArraysPerFile=100, delimiter=',',
                                                       saveAsColumns=False, verbose=verbose)
    return groupDict


def loadSavedGroupsOfPulses(outputFolder, folderList, pulseDataTypesToSave):
    groupDict = {}
    for singleFolder in folderList:
        groupDict[singleFolder] = pulseGroup()
        groupDict[singleFolder].getSavedPulses(outputFolder,
                                               pulseDataTypes=pulseDataTypesToSave,
                                               fileNamePrefix=singleFolder + '_')
    return groupDict


def removeOutlierPulses(groupDict, pulseDataTypesToRemoveOutliers):
    folderList = groupDict.keys()
    for singleFolder in folderList:
        for (pulseDataType, multiplesOfMedianStdForRejection) in pulseDataTypesToRemoveOutliers:
            groupDict[singleFolder].removeOutliers(pulseDataType, multiplesOfMedianStdForRejection)
    return groupDict


def makeGroupHistograms(groupDict,
                        pulseDataForHistogram):
    folderList = groupDict.keys()
    outHistDict = {}
    for singleFolder in folderList:

        plotFileName = os.path.join(plotFolder, "hist_" + singleFolder)
        groupDict[singleFolder].makeOutputDict(pulseDataForHistogram)
        if 'uniqueID' in pulseDataForHistogram:
            pulseDataForHistogram.remove('uniqueID')
        histogramDict = groupDict[singleFolder].outputDict
        if 'uniqueID' in histogramDict.keys():
            del histogramDict['uniqueID']
        # Histogram plotting

        outHistDict[singleFolder] = quickHistograms(histogramDict,
                                                    columns=2,
                                                    bins=histBins,
                                                    keys=pulseDataForHistogram,
                                                    errFactor=1,
                                                    plotFileName=plotFileName + 'hist',
                                                    savePlots=saveHistPlots,
                                                    doEps=False,
                                                    showPlots=showHistPlots,
                                                    verbose=verbose)
    return outHistDict


def doFindHistPeaks(outHistDict, errFactor, verbose):
    doShow = True
    folderList = groupDict.keys()
    for singleFolder in folderList:
        for key in outHistDict[singleFolder].keys():
            (hist, binCenters) = outHistDict[singleFolder][key]
            plotDict = initializeTestPlots(doShow, verbose)
            plotDict = appendToTestPlots(plotDict,
                                         hist,
                                         binCenters,
                                         legendLabel=singleFolder + ' ' + key,
                                         fmt='None',
                                         markersize=4,
                                         alpha=1.0,
                                         ls='solid',
                                         lineWidth=2)

            guessParametersSet = peakFinder(hist,
                                            binCenters,
                                            numberOfIndexesToSmoothOver=1,
                                            errFactor=errFactor,
                                            showPlot_peakFinder=False,
                                            verbose=verbose)



            for (index, (amp, mean, sigma)) in list(enumerate(guessParametersSet)):
                plotDict = appendToTestPlots(plotDict,
                                             gaussian(binCenters, amp, mean, sigma),
                                             binCenters,
                                             legendLabel=singleFolder + ' ' + key,
                                             fmt='None',
                                             markersize=4,
                                             alpha=1.0,
                                             ls=ls[index % 3],
                                             lineWidth=1)
            if plotDict['doShow']:
                quickPlotter(plotDict)
    return



if __name__ == '__main__':
    # groupDict = doExtractAndSavePulseInfo(parentFolder, folderList, outputFolder, pulseDataTypesToSave)
    groupDict = loadSavedGroupsOfPulses(outputFolder, folderList, pulseDataTypesToSave)
    groupDict = removeOutlierPulses(groupDict, pulseDataTypesToRemoveOutliers)
    outHistDict = makeGroupHistograms(groupDict,
                                   pulseDataTypesToSave)
    doFindHistPeaks(outHistDict, errFactorForPeakFinder, verbose)
