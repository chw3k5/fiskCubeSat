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
                    self.outputDict[pulseDataType].append(datum)

        # Change the data from a lists to arrays
        for pulseDataType in self.outputDict.keys():
            self.outputDict[pulseDataType] = numpy.array(self.outputDict[pulseDataType])


    def saveOutputDict(self, outPutFileBase, pulseDataTypesToSave,
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


    def filterPulses(self, pulseDataTypesForFilter):
        for (pulseType, minVal, maxVal) in pulseDataTypesForFilter:
            if maxVal < minVal:
                junk = maxVal
                maxVal = minVal
                minVal = junk
            newListOfPulsesDicts = []
            for pulseDict in self.listOfPulseDicts:
                valueToFilter = pulseDict[pulseType]
                if ((minVal <= valueToFilter), (valueToFilter <= maxVal)):
                    newListOfPulsesDicts.append(pulseDict)
            self.listOfPulseDicts = newListOfPulsesDicts


    def calcMinLen(self):
        deltaXlist = []
        lenList = []
        for pulseDict in self.listOfPulseDicts:
            lenList.append(pulseDict['deltaXIndex'])
            deltaXlist.append(pulseDict['deltaX'])
        self.minLen = numpy.min(lenList)
        self.deltaXlist = numpy.min(deltaXlist)


    def calcCharPulse(self):
        self.calcMinLen()
        numOfPulses = len(self.listOfPulseDicts)
        arrayOfAllPulses = numpy.zeros((self.minLen, numOfPulses))
        for (pulseIndex, pulseDict) in list(enumerate(self.listOfPulseDicts)):
            arrayOfAllPulses[:, pulseIndex] = pulseDict['keptData'][:self.minLen]

        self.charPulse = numpy.mean(arrayOfAllPulses, axis=1)
        print self.minLen, len(self.charPulse)













def doExtractAndSavePulseInfo(parentFolder, folderList, outputFolder, pulseDataTypesToSave,
                              smoothChannels=1,
                              numOfExponents=2,
                              showTestPlots_Pulses=False,
                              testModeReadIn=False,
                              verbose=True):
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
                                              conv_channels=smoothChannels,
                                              numOfExponents=numOfExponents,
                                              upperBoundAmp=float(1000),
                                              showTestPlots_Pulses=showTestPlots_Pulses,
                                              testModeReadIn=testModeReadIn,
                                              verbose=verbose)

        outPutFileBase = os.path.join(outputFolder, singleFolder)
        if pulseDataTypesToSave != []:
            groupDict[singleFolder].makeOutputDict(pulseDataTypesToSave)

            groupDict[singleFolder].saveOutputDict(outPutFileBase=outPutFileBase,
                                                   pulseDataTypesToSave=pulseDataTypesToSave,
                                                   maxDataArraysPerFile=100,
                                                   delimiter=',',
                                                   saveAsColumns=False,
                                                   verbose=verbose)
    return groupDict


def loadSavedGroupsOfPulses(outputFolder, folderList, pulseDataTypesToLoad):
    groupDict = {}
    for singleFolder in folderList:
        groupDict[singleFolder] = pulseGroup()
        groupDict[singleFolder].getSavedPulses(outputFolder,
                                               pulseDataTypes=pulseDataTypesToLoad,
                                               fileNamePrefix=singleFolder + '_')
    return groupDict


def removeOutlierPulses(groupDict, pulseDataTypesToRemoveOutliers):
    folderList = groupDict.keys()
    for singleFolder in folderList:
        for (pulseDataType, multiplesOfMedianStdForRejection) in pulseDataTypesToRemoveOutliers:
            groupDict[singleFolder].removeOutliers(pulseDataType, multiplesOfMedianStdForRejection)
    return groupDict


def makeGroupHistograms(groupDict,
                        pulseDataForHistogram,
                        plotFolder,
                        histBins=10,
                        saveHistPlots=False,
                        showHistPlots=False,
                        verbose=True):
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


def doFindHistPeaks(outHistDict, errFactor, smoothIndexesForPeakFinder,  verbose):
    doShow = True
    folderList = outHistDict.keys()
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
                                            numberOfIndexesToSmoothOver=smoothIndexesForPeakFinder,
                                            errFactor=errFactor,
                                            showPlot_peakFinder=True,
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


def filterPulsesForGroups(groupDict, pulseFilterDict):
    dictKeys = pulseFilterDict.keys()
    for key in dictKeys:
        groupDict[key].filterPulses(pulseFilterDict[key])
    return groupDict


def makeCharacteristicFunction(groupDict, characteristicFunctionFolders, outputFolder, verbose=True):
    for folderName in characteristicFunctionFolders:
        groupDict[folderName].calcCharPulse()
        outPutFileBase = os.path.join(outputFolder, folderName)
        saveProcessedData(['charFunction'], [groupDict[folderName].charPulse], outPutFileBase,
                          maxDataArraysPerFile=int('inf'), delimiter=',',
                          saveAsColumns=False, appendMode=False, verbose=verbose)
    return groupDict


