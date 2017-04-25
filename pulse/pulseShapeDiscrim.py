import getpass
import numpy
import os
from matplotlib import pyplot as plt

from pulse.pulseReadIn import saveProcessedData, readInSavedRowData
from pulse.pulseOperations import extractPulseInfo, removeOutliers
from peak.gaussFitter import gaussian
from peak.mariscotti import mariscotti
from quickPlots import ls, lenls



def quickHistograms(dataDict, columns=1, bins=10, keys=None,
                    errFactor=10,
                    plotFileName='hist', savePlots=False, doEps=False, showPlots=True,
                    verbose=True):
    if keys is None:
        keys = list(dataDict.keys())
    numOfSubPlots = len(keys)
    rows = int(numpy.ceil(float(numOfSubPlots)/float(columns)))
    f, axarr = plt.subplots(rows, columns)
    f.tight_layout()
    f.set_size_inches(10, 8)
    row = -1
    for (keyIndex, key) in list(enumerate(keys)):
        column = keyIndex % columns
        if column == 0:
            row += 1

        hist, bin_edges = numpy.histogram(dataDict[key], bins=bins)
        gaussParametersArray = numpy.array(mariscotti(hist, nsmooth=1,
                                                      errFactor=errFactor, plot=False, verbose=verbose))

        binCenters = [(bin_edges[n + 1] + bin_edges[n]) / 2.0 for n in range(bins)]
        binWidth = (binCenters[-1] - binCenters[0]) / float(bins)

        color = 'black'
        hatch = ''
        xlabel_str = ''
        if key == 'integral':
            xlabel_str += "Integral"
            color = 'dodgerblue'
            hatch = '/'
        elif key == 'fittedCost':
            xlabel_str += "'Cost' of fitting function"
            color = 'Crimson'
            hatch = '*'
        elif key == 'fittedAmp1':
            xlabel_str += "Fitted Amplitude 1"
            color = 'SaddleBrown'
            hatch = '|'
        elif key == 'fittedTau1':
            xlabel_str += "Fitted Tau 1"
            color = 'darkorchid'
            hatch = '\\'
        elif key == 'fittedAmp2':
            xlabel_str += "Fitted Amplitude 2"
            color = 'GoldenRod'
            hatch = 'x'
        elif key == 'fittedTau2':
            xlabel_str += "Fitted Tau 2"
            color = 'firebrick'
            hatch = 'o'
        elif key == 'fittedAmp3':
            xlabel_str += "Fitted Amplitude 3"
            color = 'forestGreen'
            hatch = '-'
        elif key == 'fittedTau3':
            xlabel_str += "Fitted Tau 3"
            color = 'Fuchsia'
            hatch = '+'
        elif key == 'fittedAmp4':
            xlabel_str += "Fitted Amplitude 4"
            color = 'Chocolate'
            hatch = '.'
        elif key == 'fittedTau4':
            xlabel_str += "Fitted Tau 4"
            color = 'Magenta'
            hatch = '0'

        if xlabel_str != '':
            xlabel_str += ' '

        axarr[row, column].set_title(xlabel_str)
        axarr[row, column].bar(binCenters, hist, binWidth, color=color, hatch=hatch)
        for (index, (amp, mean, sigma)) in list(enumerate(gaussParametersArray)):
            axarr[row, column].plot(gaussian(binCenters, amp, mean, sigma), binCenters, color='black', ls=ls[index % lenls])

    ### Save Plots ###
    if savePlots:
        plt.draw()
        if doEps:
            plotFileName += '.eps'
        else:
            plotFileName += '.png'
        if verbose:print "saving file:", plotFileName
        plt.savefig(plotFileName)

    if showPlots:
        plt.show()
    return


class pulseGroup():
    def __init__(self, listOfPulseDicts=[]):
        self.listOfPulseDicts = listOfPulseDicts

    def processPulses(self,
                      folderName,
                      fileNamePrefix='',
                      filenameSuffix='.txt',
                      columnNamesToIgnore=['time'],
                      pulseDataTypesToExtract=[],
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

        self.listOfPulseDicts.extend(extractPulseInfo(folderName=folderName,
                                                      fileNamePrefix=fileNamePrefix,
                                                      filenameSuffix=filenameSuffix,
                                                      columnNamesToIgnore=columnNamesToIgnore,
                                                      pulseDataTypesToExtract=pulseDataTypesToExtract,
                                                      skipRows=skipRows,
                                                      delimiter=delimiter,
                                                      trimBeforeMin=trimBeforeMin,
                                                      multiplesOfMedianStdForRejection=multiplesOfMedianStdForRejection, # None or float, None means no rejection
                                                      conv_channels=conv_channels,
                                                      numOfExponents=numOfExponents,
                                                      upperBoundAmp=upperBoundAmp,
                                                      showTestPlots_Pulses=showTestPlots_Pulses,
                                                      testModeReadIn=testModeReadIn,
                                                      verbose=verbose)
                                     )


    def getSavedPulses(self,
                       folderName,
                       pulseDataTypes,
                       fileNamePrefix='',
                       filenameSuffix='.csv'):
        listOfPulseDicts = self.listOfPulseDicts
        for pulseDataType in pulseDataTypes:
            fileName = os.path.join(folderName, fileNamePrefix + pulseDataType + filenameSuffix)

            listOfPulseDicts = readInSavedRowData(fileName, pulseDataType, listOfPulseDicts)
        self.listOfPulseDicts = listOfPulseDicts


    def makeOutputDict(self, pulseDataTypesToExtract):
        self.outputDict = {}
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
                    except TypeError:
                        self.outputDict[pulseDataType].append(datum)
        # Change the data from a lists to arrays
        for pulseDataType in self.outputDict.keys():
            self.outputDict[pulseDataType] = numpy.array(self.outputDict[pulseDataType])


    def saveOutputDict(self, outPutFileBase, saveDataType,
                       maxDataArraysPerFile=100, delimiter=',',
                       saveAsColumns=False, verbose=True):
        for saveDataType in pulseDataTypesToSave:
            listOfHeaderNames = self.outputDict['uniqueID']
            listOfDataArrays = self.outputDict[saveDataType]
            fileBaseName = outPutFileBase + '_' + saveDataType
            saveProcessedData(listOfHeaderNames, listOfDataArrays, fileBaseName,
                              maxDataArraysPerFile=maxDataArraysPerFile, delimiter=delimiter,
                              saveAsColumns=saveAsColumns, verbose=verbose)


    def removeOutliers(self, parameter, multiplesOfMedianStdForRejection=5.0):
        self.makeOutputDict([parameter])
        costArray = self.outputDict[parameter]
        costArray, keepMask = removeOutliers(costArray,
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
folderList = [
    'CHC alpha traces',
    'CHC alpha traces thrsh 180',
    'CHC alpha_gamma traces',
    'CHC gamma traces']
numOfExponents = 2
pulseDataTypesToExtract = ['integral', 'fittedCost']
for index in range(numOfExponents):
    pulseDataTypesToExtract.extend(['fittedAmp' + str(index + 1), 'fittedTau' + str(index + 1)]) # this turn into keys for a dictionary that extractPulseInfo Outputs
pulseDataForHistogram = pulseDataTypesToExtract[:]
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


def doExtractAndSavePulseInfo(parentFolder, folderList, outputFolder):
    groupDict = {}
    for singleFolder in folderList:
        folderName = os.path.join(parentFolder, singleFolder)
        aGroupOfPulses = pulseGroup()
        aGroupOfPulses.processPulses(folderName=folderName,
                                     fileNamePrefix=singleFolder + '_',
                                     filenameSuffix='.txt',
                                     columnNamesToIgnore=['time'],
                                     pulseDataTypesToExtract=pulseDataTypesToExtract,
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
            aGroupOfPulses.makeOutputDict(pulseDataTypesToExtract)
            for saveDataType in pulseDataTypesToSave:
                aGroupOfPulses.saveOutputDict(outPutFileBase=outPutFileBase, saveDataType=saveDataType,
                                              maxDataArraysPerFile=100, delimiter=',',
                                              saveAsColumns=False, verbose=verbose)
        groupDict[singleFolder] = aGroupOfPulses
    return groupDict


def loadSavedGroupsOfPulses(outputFolder, folderList):
    groupDict = {}
    for singleFolder in folderList:
        aGroupOfPulses = pulseGroup()
        aGroupOfPulses.getSavedPulses(outputFolder,
                                      pulseDataTypes=pulseDataTypesToSave,
                                      fileNamePrefix=singleFolder + '_')

        groupDict[singleFolder] = aGroupOfPulses
    return groupDict


def makeGroupHistograms(groupDict,
                        pulseDataTypesToRemoveOutliers,
                        pulseDataTypesToExtract):
    folderList = groupDict.keys()
    for singleFolder in folderList:
        aGroupOfPulses = groupDict[singleFolder]
        for (pulseDataType, multiplesOfMedianStdForRejection) in pulseDataTypesToRemoveOutliers:
            aGroupOfPulses.removeOutliers(pulseDataType, multiplesOfMedianStdForRejection)
        aGroupOfPulses.makeOutputDict(pulseDataTypesToExtract)


        plotFileName = os.path.join(plotFolder, "hist_" + singleFolder)
        histogramDict = aGroupOfPulses.outputDict
        if 'uniqueID' in histogramDict.keys():
            del histogramDict['uniqueID']
        # Histogram plotting
        quickHistograms(histogramDict, columns=2, bins=histBins, keys=pulseDataForHistogram,
                        errFactor=0,
                        plotFileName=plotFileName + 'hist', savePlots=saveHistPlots, doEps=False,
                        showPlots=showHistPlots,
                        verbose=verbose)
    return
    # for pulseDataType in histogramDict.keys():
    #     hist, bin_edges = numpy.histogram(histogramDict[pulseDataType], bins=histBins)
    #     gaussParametersArray = numpy.array(mariscotti(hist, nsmooth=3,
    #                                                   errFactor=0, plot=showPeakFinderPlot, verbose=verbose))



if __name__ == '__main__':
    # groupDict = doExtractAndSavePulseInfo(parentFolder, folderList, outputFolder)
    groupDict = loadSavedGroupsOfPulses(outputFolder, folderList)
    makeGroupHistograms(groupDict,
                        pulseDataTypesToRemoveOutliers,
                        pulseDataTypesToExtract)
